from matplotlib import pyplot as plt
import os, re
from PIL import Image
import numpy as np
import torchvision
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchsummary import summary
from keras import Sequential
from keras import layers
from keras import utils


# (x_train, y_train), (x_test, y_test) = cifar10.load_data()
class VGG19BN(nn.Module):
    def __init__(self):
        super(VGG19BN, self).__init__()
        self.vgg19_bn = torchvision.models.vgg19_bn(num_classes=10)
        self.features = self.vgg19_bn.features
        self.classifier = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(True),
            nn.BatchNorm1d(128),
            nn.Dropout(),
            nn.Linear(128, 10),
        )
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.classifier:
            if isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, mean=0, std=0.02)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def loadClick(self):
    self.load_filenameForQ5 = str(QFileDialog.getOpenFileName(self, "Choose a file")[0])
    print(self.load_filenameForQ5)


def augmentClick(self):
    self.loadAllFile = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
    print(self.loadAllFile)
    overall = [i for i in os.listdir(self.loadAllFile) if re.search(".png", i)]
    self.files = overall
    print(self.files)
    for i in range(9):
        img = Image.open(self.loadAllFile + "/" + self.files[i])

        data_augmentation1 = Sequential(
            [
                layers.RandomFlip(),
            ]
        )
        data_augmentation2 = Sequential(
            [
                layers.RandomRotation(10),
            ]
        )
        data_augmentation3 = Sequential(
            [
                layers.Rescaling(0.5),
            ]
        )
        fig = plt.figure()
        plt.subplot(1, 4, 1)
        plt.axis("off")
        plt.imshow(img)

        img = utils.img_to_array(img)

        plt.subplot(1, 4, 2)
        plt.axis("off")
        flip = data_augmentation1(img)
        flip = Image.fromarray(flip.numpy().astype(np.uint8))
        plt.imshow(flip)

        plt.subplot(1, 4, 3)
        plt.axis("off")
        rotate = data_augmentation2(img)
        rotate = Image.fromarray(rotate.numpy().astype(np.uint8))
        plt.imshow(rotate)

        plt.subplot(1, 4, 4)
        plt.axis("off")
        crop = data_augmentation3(img)
        crop = Image.fromarray(crop.numpy().astype(np.uint8))
        print(crop.size)
        plt.imshow(crop)
        plt.title(self.files[i])
        plt.show()


def structClick():
    modelSTR = models.vgg19_bn()
    summary(modelSTR)


def accClick(self):
    img = Image.open("./5-4.png")
    plt.figure()
    plt.imshow(img)
    plt.axis("off")
    plt.show()


def inferClick(self):
    net = VGG19BN().to("cpu")
    checkpoint = torch.load(
        "vgg19_bn.pth", map_location="cpu"
    )  # Load the trained model weights
    net.load_state_dict(checkpoint, strict=False)
    net.eval()  # Set the model to evaluation mode

    def infer_and_visualize(model, imagePath):
        class_names = [
            "airplane",
            "automobile",
            "bird",
            "cat",
            "deer",
            "dog",
            "frog",
            "horse",
            "ship",
            "truck",
        ]

        transform = transforms.Compose(
            [
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(10),
                transforms.RandomCrop(32, padding=4),
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                ),
            ]
        )
        image = Image.open(imagePath)
        image = transform(image).unsqueeze(0)  # Add a batch dimension

        with torch.no_grad():
            outputs = model(image)
            predicted = torch.argmax(outputs, dim=1)

            # plt.imshow(image[0].permute(1, 2, 0).numpy())
            # plt.title(f"Predicted: {class_names[predicted.item()]}")
            # plt.show()
            self.mypixmap = QPixmap()
            self.mypixmap.load(self.load_filenameForQ5)
            self.mypixmap.scaled(128, 128)
            # print(self.load_filenameForQ5)
            self.label_2.setPixmap(self.mypixmap)
            self.label.setText("Predicted: " + class_names[predicted.item()])

            # Visualize the predicted class distribution
            predicted_probs = torch.softmax(outputs, dim=1)
            predicted_probs = predicted_probs.numpy()[0]  # Convert to NumPy array
            plt.bar(range(10), predicted_probs)
            plt.xticks(range(10), class_names, rotation=45)
            plt.title("Class Distribution")
            plt.show()

    # Call the function with the model and the path to your custom test image
    imagePath = self.load_filenameForQ5
    print("path: " + imagePath)
    infer_and_visualize(net, imagePath)
