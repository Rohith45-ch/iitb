#!/usr/bin/env python3
"""
NVIDIA PilotNet End-to-End Steering Neural Network Generator & Exporter.
Builds the complete PilotNet architecture into an optimized ONNX model
(models/pilotnet_steering.onnx) for low-latency steering inference on Raspberry Pi 4B.
"""

from pathlib import Path
import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_MODEL_PATH = PROJECT_ROOT / "models" / "pilotnet_steering.onnx"


def create_initializer(name: str, tensor_array: np.ndarray) -> onnx.TensorProto:
    """Helper to convert numpy array into ONNX TensorProto initializer."""
    return helper.make_tensor(
        name=name,
        data_type=TensorProto.FLOAT,
        dims=list(tensor_array.shape),
        vals=tensor_array.flatten().tolist(),
    )


def build_pilotnet_onnx(output_path: Path):
    """
    Constructs the NVIDIA PilotNet computational graph:
    Input: [1, 3, 66, 200]
    Conv1: (24, 3, 5, 5), Stride 2 -> ReLU -> [1, 24, 31, 98]
    Conv2: (36, 24, 5, 5), Stride 2 -> ReLU -> [1, 36, 14, 47]
    Conv3: (48, 36, 5, 5), Stride 2 -> ReLU -> [1, 48, 5, 22]
    Conv4: (64, 48, 3, 3), Stride 1 -> ReLU -> [1, 64, 3, 20]
    Conv5: (64, 64, 3, 3), Stride 1 -> ReLU -> [1, 64, 1, 18]
    Flatten: 1152
    Dense1: (1152, 100) -> ReLU
    Dense2: (100, 50) -> ReLU
    Dense3: (50, 10) -> ReLU
    Dense4: (10, 1) -> Tanh -> Output steering angle delta in [-1.0, 1.0]
    """
    np.random.seed(42)

    # Initializers (Weights & Biases with Xavier initialization)
    w_conv1 = np.random.randn(24, 3, 5, 5).astype(np.float32) * np.sqrt(2.0 / (3 * 25))
    b_conv1 = np.zeros(24, dtype=np.float32)

    w_conv2 = np.random.randn(36, 24, 5, 5).astype(np.float32) * np.sqrt(2.0 / (24 * 25))
    b_conv2 = np.zeros(36, dtype=np.float32)

    w_conv3 = np.random.randn(48, 36, 5, 5).astype(np.float32) * np.sqrt(2.0 / (36 * 25))
    b_conv3 = np.zeros(48, dtype=np.float32)

    w_conv4 = np.random.randn(64, 48, 3, 3).astype(np.float32) * np.sqrt(2.0 / (48 * 9))
    b_conv4 = np.zeros(64, dtype=np.float32)

    w_conv5 = np.random.randn(64, 64, 3, 3).astype(np.float32) * np.sqrt(2.0 / (64 * 9))
    b_conv5 = np.zeros(64, dtype=np.float32)

    flat_size = 64 * 1 * 18  # 1152
    w_fc1 = np.random.randn(flat_size, 100).astype(np.float32) * np.sqrt(2.0 / flat_size)
    b_fc1 = np.zeros(100, dtype=np.float32)

    w_fc2 = np.random.randn(100, 50).astype(np.float32) * np.sqrt(2.0 / 100)
    b_fc2 = np.zeros(50, dtype=np.float32)

    w_fc3 = np.random.randn(50, 10).astype(np.float32) * np.sqrt(2.0 / 50)
    b_fc3 = np.zeros(10, dtype=np.float32)

    w_fc4 = np.random.randn(10, 1).astype(np.float32) * np.sqrt(2.0 / 10)
    b_fc4 = np.zeros(1, dtype=np.float32)

    initializers = [
        create_initializer("W_conv1", w_conv1),
        create_initializer("B_conv1", b_conv1),
        create_initializer("W_conv2", w_conv2),
        create_initializer("B_conv2", b_conv2),
        create_initializer("W_conv3", w_conv3),
        create_initializer("B_conv3", b_conv3),
        create_initializer("W_conv4", w_conv4),
        create_initializer("B_conv4", b_conv4),
        create_initializer("W_conv5", w_conv5),
        create_initializer("B_conv5", b_conv5),
        create_initializer("W_fc1", w_fc1),
        create_initializer("B_fc1", b_fc1),
        create_initializer("W_fc2", w_fc2),
        create_initializer("B_fc2", b_fc2),
        create_initializer("W_fc3", w_fc3),
        create_initializer("B_fc3", b_fc3),
        create_initializer("W_fc4", w_fc4),
        create_initializer("B_fc4", b_fc4),
    ]

    nodes = [
        helper.make_node("Conv", ["input_image", "W_conv1", "B_conv1"], ["conv1_out"], strides=[2, 2]),
        helper.make_node("Relu", ["conv1_out"], ["relu1_out"]),

        helper.make_node("Conv", ["relu1_out", "W_conv2", "B_conv2"], ["conv2_out"], strides=[2, 2]),
        helper.make_node("Relu", ["conv2_out"], ["relu2_out"]),

        helper.make_node("Conv", ["relu2_out", "W_conv3", "B_conv3"], ["conv3_out"], strides=[2, 2]),
        helper.make_node("Relu", ["conv3_out"], ["relu3_out"]),

        helper.make_node("Conv", ["relu3_out", "W_conv4", "B_conv4"], ["conv4_out"], strides=[1, 1]),
        helper.make_node("Relu", ["conv4_out"], ["relu4_out"]),

        helper.make_node("Conv", ["relu4_out", "W_conv5", "B_conv5"], ["conv5_out"], strides=[1, 1]),
        helper.make_node("Relu", ["conv5_out"], ["relu5_out"]),

        helper.make_node("Flatten", ["relu5_out"], ["flat_out"], axis=1),

        helper.make_node("Gemm", ["flat_out", "W_fc1", "B_fc1"], ["fc1_out"]),
        helper.make_node("Relu", ["fc1_out"], ["relu_fc1_out"]),

        helper.make_node("Gemm", ["relu_fc1_out", "W_fc2", "B_fc2"], ["fc2_out"]),
        helper.make_node("Relu", ["fc2_out"], ["relu_fc2_out"]),

        helper.make_node("Gemm", ["relu_fc2_out", "W_fc3", "B_fc3"], ["fc3_out"]),
        helper.make_node("Relu", ["fc3_out"], ["relu_fc3_out"]),

        helper.make_node("Gemm", ["relu_fc3_out", "W_fc4", "B_fc4"], ["steering_linear"]),
        helper.make_node("Tanh", ["steering_linear"], ["steering_angle"]),
    ]

    inputs = [
        helper.make_tensor_value_info("input_image", TensorProto.FLOAT, [1, 3, 66, 200])
    ]
    outputs = [
        helper.make_tensor_value_info("steering_angle", TensorProto.FLOAT, [1, 1])
    ]

    graph = helper.make_graph(
        nodes=nodes,
        name="PilotNetSteering",
        inputs=inputs,
        outputs=outputs,
        initializer=initializers,
    )

    model = helper.make_model(
        graph,
        producer_name="UAMC_IITB_PilotNet",
        opset_imports=[helper.make_opsetid("", 13)],
        ir_version=10,
    )
    onnx.checker.check_model(model)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, str(output_path))
    size_kb = output_path.stat().st_size / 1024
    print(f"[PilotNetExporter] Successfully exported PilotNet ONNX model to: {output_path} ({size_kb:.1f} KB)")


def verify_pilotnet_inference(model_path: Path):
    """Verifies forward pass with random camera input."""
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    dummy_input = np.random.randn(1, 3, 66, 200).astype(np.float32)
    output = session.run(None, {"input_image": dummy_input})[0]
    steering_val = float(output[0, 0])
    print(f"[PilotNetExporter] Verification inference successful! Sample steering: {steering_val:+.4f} (range: [-1.0, 1.0])")


def main():
    print("=" * 65)
    print("  UAMC IIT Bombay — PilotNet End-to-End Steering Exporter")
    print("=" * 65)
    build_pilotnet_onnx(OUTPUT_MODEL_PATH)
    verify_pilotnet_inference(OUTPUT_MODEL_PATH)


if __name__ == "__main__":
    main()
