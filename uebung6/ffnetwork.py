import torch
import torch.nn as nn
import torch.types


class FeedForwardNetwork(nn.Module):
    """
    Class for creating a feed forward Network.
    """

    def __init__(self, input_layer: int, hidden_layer1: int, hidden_layer2: int, output_layer: int,
                 dropout_rate=None) -> None:
        super(FeedForwardNetwork, self).__init__()

        self.input_size = input_layer
        self.hidden_size1 = hidden_layer1
        self.hidden_size2 = hidden_layer2
        self.output_size = output_layer
        self.dropout_rate = dropout_rate

        # defining the layers
        self.l1 = nn.Linear(self.input_size, self.hidden_size1)
        self.l2 = nn.Linear(self.hidden_size1, self.hidden_size2)
        self.l3 = nn.Linear(self.hidden_size2, self.output_size)

        # defining the dropout rate
        if dropout_rate is not None:
            self.dropout = nn.Dropout(dropout_rate)
        else:
            self.dropout = nn.Dropout(0.0)

        # defining the activation function
        self.relu = nn.ReLU()

    def forward(self, x):
        """
        Apply all layers on sample x.
        """
        out = self.l1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.l3(out)  # no softmax here -> cross entropy function will do that
        return out


def train_eval_nn(model: FeedForwardNetwork, train_loader: torch.utils.data.DataLoader,
                  dev_loader: torch.utils.data.DataLoader, \
                  test_loader: torch.utils.data.DataLoader, epochs: int, loss_function: str, optimizer, device: str,
                  training: bool) -> FeedForwardNetwork:
    """
    Calls train_nn and eval_nn functions for number of epochs defined in epochs parameter.
    :rtype: FeedForwardNetwork
"""

    train_nn(model, train_loader, loss_function, optimizer, device, epochs)
    evaluation = eval_nn(model, dev_loader)
    if training:
        print("Evaluate on test data")
        eval_nn(model, train_loader)

    return model, evaluation


def train_nn(model: FeedForwardNetwork, data_loader: torch.utils.data.DataLoader, loss_function: str, optimizer,
             device: str, epochs: int):
    """
    Train the network with passed data from data_loader.
    """
    i = 1
    for epoch in range(epochs):
        print("\n**************************************************************")
        print("Epoch ", i)
        print("**************************************************************\n")

        model.train()
        batchloss = 0
        for batch, (features, targets) in enumerate(data_loader):
            optimizer.zero_grad()
            features = features.to(device)
            targets = targets.to(device)

            # do forward propagation and calculate the loss
            out = model.forward(features.float())
            loss = loss_function(out, targets)
            batchloss += loss

            # do back propagation
            loss.backward()
            optimizer.step()

        i += 1


def eval_nn(model: FeedForwardNetwork, data_loader: torch.utils.data.DataLoader):
    """
    Evaluate the network with passed data from data_loader.
    Source of that function: Musterlösung Übung 5
    """

    model.eval()
    correct = 0
    total = 0
    goldlabcount = [0, 0, 0]
    predlabcount = [0, 0, 0]
    trueposcount = [0, 0, 0]
    with torch.no_grad():
        for data in data_loader:
            # Every data have a vector[min, max or avg] and a sentiment classification
            nptweet, labels = data
            # compute the prediction with the trained NN
            outputs = model(nptweet.float())
            _, predicted = torch.max(outputs.data, 1)
            for valid in range(len(labels)):
                # Note: Changed Classes to 0: negative, 1: neutral, 2: positive
                # Number of Gold labels
                goldlabcount[labels[valid]] += 1
                # Number of predicted labels
                predlabcount[predicted[valid]] += 1
                if labels[valid] == predicted[valid]:
                    trueposcount[labels[valid]] += 1
            total += labels.size(0)
            # Number of correct predicted labels
            correct += (predicted == labels).sum().item()

    print("Gold: ", goldlabcount)
    print("Predicted: ", predlabcount)
    print("True Positive: ", trueposcount)
    precision = list()
    recall = list()
    f1score = list()
    for ids in range(len(trueposcount)):
        # prevents division zero
        if trueposcount[ids] != 0 and predlabcount[ids] != 0:
            precision.append(trueposcount[ids] / predlabcount[ids])
            recall.append(trueposcount[ids] / goldlabcount[ids])
            f1score.append(2 * ((precision[ids] * recall[ids]) / (precision[ids] + recall[ids])))
        else:
            precision.append(0.0)
            recall.append(0.0)
            f1score.append(0.0)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1-Score[negativ, neutral, positiv]: ", f1score)
    print("Correct predicted total:", correct)
    print("Number of predictions/tweets:", total)
    accuracy = 100 * correct / total
    print('Accuracy of the network on the test set: %d %%' % accuracy)
    return goldlabcount, predlabcount, trueposcount, precision, recall, f1score, accuracy
