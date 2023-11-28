import torch
import torchvision.transforms as transforms
import torchvision.datasets as dset
import os

# Directory containing the data.


def get_data(projectName, params):
    """
    Loads the dataset and applies proproccesing steps to it.
    Returns a PyTorch DataLoader.

    """
    target_dir = 'gmModel_DC/user_dataset/'+projectName+'/'+projectName
    # root = 'gmModel_DC/user_dataset/'+params['projectName']+'/'+params['projectName']

    # Data proprecessing.
    transform = transforms.Compose([
        transforms.Resize(params['imsize']),
        transforms.CenterCrop(params['imsize']),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5),
            (0.5, 0.5, 0.5))])

    # Create the dataset.
    dataset = dset.ImageFolder(root=target_dir, transform=transform)

    # Create the dataloader.
    dataloader = torch.utils.data.DataLoader(dataset,
        batch_size=params['bsize'],
        shuffle=True)

    return dataloader