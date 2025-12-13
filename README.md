# 👁️ EyeCommand OS

**EyeCommand OS** is a touchless biometric control system powered by Computer Vision. This system allows users to authenticate and execute computer commands (such as opening YouTube, launching applications, or shutting down the system) using only **hand gestures** and **eye blinks**.

![EyeCommand Demo Simulation](assets/demo.gif)

Built with **Python**, **OpenCV**, and **MediaPipe**.

## ✨ Key Features

  * **Hand Gesture Activation:** Utilizes a specific "Thumbs Up" gesture to activate the input mode, preventing accidental triggers.
  * **Wink-Based Password:** Uses left and right eye blinks as binary input codes (`0` and `1`).
  * **Multi-Command Support:** Supports multiple code combinations for different actions (e.g., Login, Automation, Shutdown).
  * **JSON Configuration:** All settings (passwords, sensitivity, delay, actions) are decoupled in a `config.json` file for easy modification without touching the code.
  * **Automated Actions:** Integrated with `webbrowser` and `pyautogui` to open links, toggle fullscreen, or control system functions automatically.
  * **Visual Feedback UI:** A futuristic interface with code slot indicators, cooldown status, and validation results.

## 🛠️ Tech Stack

  * [Python 3.x](https://www.python.org/)
  * [OpenCV](https://opencv.org/) - For real-time computer vision and image processing.
  * [MediaPipe](https://www.google.com/search?q=https://google.github.io/mediapipe/) - For robust Face Mesh and Hand Landmark detection.
  * [PyAutoGUI](https://pyautogui.readthedocs.io/) - For programmatic keyboard and mouse control.

## ⚙️ Installation

1.  **Clone this repository** to your local machine.

2.  **Install the required dependencies:**
    Open your terminal or command prompt and run:

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: Standard libraries like `json`, `math`, `time`, `os`, and `webbrowser` are pre-installed with Python).*

3.  **Configuration Setup:**
    Ensure the `config.json` file is located in the same directory as the main script (`main.py`).

## 📝 Configuration (`config.json`)

You can customize your passcodes and actions via the `config.json` file. Here is the default structure:

```json
{
    "max_digit": 6,
    "blink_threshold": 0.24,
    "input_delay": 1.0,
    "reset_delay": 3.0,
    "commands": [
        {
            "name": "WATCH YOUTUBE",
            "code": [0, 1, 0, 1, 0, 1],
            "action_id": "play_youtube"
        },
        {
            "name": "TERMINATE APP",
            "code": [0, 0, 1, 1, 0, 0],
            "action_id": "terminate_app"
        }
    ]
}
```

**Parameters:**

  * `code`: A 6-digit combination. **0 = Left Wink**, **1 = Right Wink**.
  * `blink_threshold`: Eye sensitivity (Lower value = requires tighter blink). Default: `0.24`.
  * `input_delay`: Cooldown time (in seconds) between blinks to prevent double inputs.
  * `action_id`: A unique ID mapped to specific Python functions in the main script.

## 🚀 How to Use

1.  Run the application:
    ```bash
    python main.py
    ```
2.  **Standby Mode (Locked):** Show a **Thumbs Up** gesture to the camera to unlock the system. Ensure your other four fingers are folded.
3.  **Input Mode:**
      * Wink **Left Eye** to input **0**.
      * Wink **Right Eye** to input **1**.
      * Wait for the "READY" indicator (Green) before inputting the next digit.
4.  **Execution:**
      * If the code matches (e.g., `010101`), the system will execute the corresponding action (e.g., Open Browser).
      * If the code is `001100`, the program will terminate (*Kill Switch*).

## ⚠️ Troubleshooting

  * **Eyes not detected?**
    Ensure you are in a well-lit environment. Thick eyeglass frames might interfere with the mesh detection.
  * **Double Inputs?**
    Increase the `input_delay` value in `config.json` to `1.5` or `2.0`.
  * **Thumb gesture not working?**
    Make sure your index, middle, ring, and pinky fingers are fully folded down (knuckles higher than fingertips).

## 👨‍💻 Author

**Arizal Firdaus**
*IT Student & Machine Learning & Deep Learning Engineer*

## 📄 License

This project is distributed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

You are free to use, modify, and distribute this code for educational or development purposes.

-----

*This project was created for educational purposes in Computer Vision and Human-Computer Interaction (HCI).*