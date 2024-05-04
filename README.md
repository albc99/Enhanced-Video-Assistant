# Enhanced Video Assistant (EVA)
[![Python](https://img.shields.io/badge/Python-%233776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![ReactJS](https://img.shields.io/badge/ReactJS-%2361DAFB.svg?style=flat-square&logo=react&logoColor=white)](https://reactjs.org/)
[![Azure](https://img.shields.io/badge/Azure-%230078D4.svg?style=flat-square&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![OpenAI Whisper](https://img.shields.io/badge/Whisper-%23000000.svg?style=flat-square)]([https://openai.com/whisper](https://openai.com/research/whisper))
[![CleanVoiceAI](https://img.shields.io/badge/CleanVoiceAI-%2318774B.svg?style=flat-square)](https://cleanvoice.ai/)
[![OpenAI GPT](https://img.shields.io/badge/OpenAI%20GPT-%23556B2F.svg?style=flat-square&logo=openai&logoColor=white)](https://openai.com/chatgpt)
[![FastAPI](https://img.shields.io/badge/FastAPI-%23007DAD.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vite](https://img.shields.io/badge/Vite-%2364b587.svg?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-%23EFEFEF.svg?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)

EVA is an automated video editing web application designed to streamline video production processes with AI-powered features. It enhances user engagement and video quality with minimal effort.

## Key Features

- **Video Streamliner**: Automatically identifies and extracts pivotal moments from videos. It provides editable timestamps to refine the cuts manually.

- **Narration Improver**: Enhances audio quality by pinpointing moments with stuttering, dead air, and other audio defects for correction.

- **Focus Group**: Simulates an AI-driven audience to provide feedback on video tone, engagement, and clarity. Includes a chat feature for interactive learning about video enhancement techniques and application usage.

## Access the Application

**Web Application URL**: [EVA on Azure](http://enhancedvideoassistant.azurewebsites.net)

**Note**: The application is currently accessible via HTTP only; HTTPS is not supported. If you can't log in make sure that the url is HTTP, sometimes your browser defaults to HTTPS even though the link is HTTP.

## Prerequisites

- Docker installed on your machine.
- Python 3.8.
- Support for `msodbc` on your device.
- Wget installed on your machine

### Downloading wget:
#### Mac OS:
Install homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Install wget:
```bash
brew install wget
```

### Windows:
Download the latest version of Wget from: https://gnuwin32.sourceforge.net/packages/wget.htm

Follow the instruction (https://gnuwin32.sourceforge.net/install.html) for installing Wget


## 🛠 Installation Instructions

Clone the repository and set up the web and backend services:

```bash
git clone https://github.com/TechSmith/CSE498-Spring2024.git
cd CSE498-Spring2024
```

### Setting Up the Frontend
```bash
cd eva-web-app
npm install
```

### Setting Up the Backend
```bash
cd eva-fastapi-backend
mkdir -p models

# Download pretrained whisper models
wget -P models/ https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt
wget -P models/ https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt
wget -P models/ https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt

# Build docker container
docker build -t eva-backend .
```

## 🚕 Usage Instructions
### Run Frontend Server:

#### In terminal 1:
```bash
cd eva-web-app
npm run dev
```

#### In terminal 2:
```bash
cd eva-fastapi-backend

# Run docker container. Note the docker container must have built succesfully in installation process 
docker run -p 80:80 eva-backend
```

### Accessing the Web Application
- #### Web Interface: 
    ```bash
    http://localhost:5173
    ```
- #### API Documentation:
    ```bash
    #Fast API UI for API interaction documentation
    http://localhost/docs
    ```

##
This comprehensive `README.md` file encapsulates everything needed to get started with the Enhanced Video Assistant, from installation to everyday use, all structured for ease of understanding and effectiveness.

