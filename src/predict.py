from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import mobilenet_v3_small


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "trashbin_fill_monitor_mobilenetv3.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model_bundle():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di:\n{MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    class_names = checkpoint.get(
        "class_names",
        ["empty", "half-full", "full"],
    )

    img_size = checkpoint.get("img_size", 192)

    mean = checkpoint.get(
        "mean",
        [0.485, 0.456, 0.406],
    )

    std = checkpoint.get(
        "std",
        [0.229, 0.224, 0.225],
    )

    priority_map = checkpoint.get(
        "priority_map",
        {
            "empty": {
                "status": "LOW",
                "action": "Belum perlu diangkut",
                "priority_score": 1,
            },
            "half-full": {
                "status": "MEDIUM",
                "action": "Pantau / jadwalkan",
                "priority_score": 2,
            },
            "full": {
                "status": "HIGH",
                "action": "Prioritaskan pengangkutan",
                "priority_score": 3,
            },
        },
    )

    model = mobilenet_v3_small(weights=None)

    model.classifier[-1] = nn.Linear(
        model.classifier[-1].in_features,
        len(class_names),
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = model.to(DEVICE)
    model.eval()

    transform = transforms.Compose(
        [
            transforms.Resize(
                (img_size, img_size)
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=mean,
                std=std,
            ),
        ]
    )

    return {
        "model": model,
        "class_names": class_names,
        "img_size": img_size,
        "priority_map": priority_map,
        "transform": transform,
        "device": DEVICE,
        "validation_f1": checkpoint.get(
            "best_validation_macro_f1"
        ),
    }


def predict_image(image: Image.Image, bundle: dict):
    model = bundle["model"]
    transform = bundle["transform"]
    class_names = bundle["class_names"]
    priority_map = bundle["priority_map"]
    device = bundle["device"]

    image = image.convert("RGB")

    tensor = transform(image)
    tensor = tensor.unsqueeze(0)
    tensor = tensor.to(device)

    with torch.no_grad():
        logits = model(tensor)

        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

    probs_cpu = probabilities.cpu()

    pred_idx = int(
        torch.argmax(
            probs_cpu
        ).item()
    )

    label = class_names[pred_idx]
    confidence = float(
        probs_cpu[pred_idx].item()
    )

    all_probabilities = {
        class_names[i]: float(
            probs_cpu[i].item()
        )
        for i in range(
            len(class_names)
        )
    }

    priority = priority_map.get(
        label,
        {
            "status": "UNKNOWN",
            "action": "Perlu pemeriksaan manual",
            "priority_score": 0,
        },
    )

    return {
        "label": label,
        "confidence": confidence,
        "probabilities": all_probabilities,
        "priority": priority,
    }