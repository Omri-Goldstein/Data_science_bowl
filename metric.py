import numpy as np


def score_image(labels, y_pred):
    true_objects = len(np.unique(labels))
    pred_objects = len(np.unique(y_pred))

    intersection = np.histogram2d(labels.flatten(), y_pred.flatten(), bins=(true_objects, pred_objects))[0]

    area_true = np.histogram(labels, bins=true_objects)[0]
    area_pred = np.histogram(y_pred, bins=pred_objects)[0]
    area_true = np.expand_dims(area_true, -1)
    area_pred = np.expand_dims(area_pred, 0)

    union = area_true + area_pred - intersection

    intersection = intersection[1:, 1:]
    union = union[1:, 1:]
    union[union == 0] = 1e-9

    iou = intersection / union

    prec = []
    for t in np.arange(0.5, 1.0, 0.05):
        tp, fp, fn = precision_at(t, iou)
        p = np.true_divide(tp, (tp + fp + fn))
        # print("{:1.3f}\t{}\t{}\t{}\t{:1.3f}".format(t, tp, fp, fn, p))
        prec.append(p)

    return np.mean(prec)


def precision_at(threshold, iou):
    matches = iou > threshold
    true_positives = np.sum(matches, axis=1) == 1  # Correct objects
    false_positives = np.sum(matches, axis=0) == 0  # Missed objects
    false_negatives = np.sum(matches, axis=1) == 0  # Extra objects
    tp, fp, fn = np.sum(true_positives), np.sum(false_positives), np.sum(false_negatives)
    return tp, fp, fn


if __name__ == '__main__':
    import skimage.io
    import matplotlib.pyplot as plt
    import skimage.segmentation

    # Load a single image and its associated masks
    id = '0a7d30b252359a10fd298b638b90cb9ada3acced4e0c0e5a3692013f432ee4e9'
    file = "C:\Users\omri\Personal\Kaggle\Project/stage1_train/{}/images/{}.png".format(id, id)
    masks = "C:\Users\omri\Personal\Kaggle\Project/stage1_train/{}/masks/*.png".format(id)
    image = skimage.io.imread(file)
    masks = skimage.io.imread_collection(masks).concatenate()
    height, width, _ = image.shape
    num_masks = masks.shape[0]

    # Make a ground truth label image (pixel value is index of object label)
    labels = np.zeros((height, width), np.uint16)
    for index in range(0, num_masks):
        labels[masks[index] > 0] = index + 1

    # Show label image
    fig = plt.figure()
    plt.imshow(image)
    plt.title("Original image")
    fig = plt.figure()
    plt.imshow(labels)
    plt.title("Ground truth masks")
    plt.show()

    # Simulate an imperfect submission
    offset = 2  # offset pixels
    y_pred = labels[offset:, offset:]
    y_pred = np.pad(y_pred, ((0, offset), (0, offset)), mode="constant")
    y_pred[y_pred == 20] = 0  # Remove one object
    y_pred, _, _ = skimage.segmentation.relabel_sequential(y_pred)  # Relabel objects

    # Show simulated predictions
    fig = plt.figure()
    plt.imshow(y_pred)
    plt.title("Simulated imperfect submission")
    plt.show()

    print(score_image(labels, y_pred))
    print('exprected score: 0.33510....')
