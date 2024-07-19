## About Amazon Connect Admin Console Tool
This solution can be used to delete resources in Amazon Connect.

### Installation

Clone the repo

```bash
git clone https://github.com/photosphere/connect-console.git
```

cd into the project root folder

```bash
cd connect-console
```

#### Create virtual environment

##### via python

Then you should create a virtual environment named .venv

```bash
python -m venv .venv
```

and activate the environment.

On Linux, or OsX 

```bash
source .venv/bin/activate
```
On Windows

```bash
source.bat
```

Then you should install the local requirements

```bash
pip install -r requirements.txt
```
### Build and run the Application Locally

```bash
streamlit run contact_console.py
```

### Or Build and run the Application on Cloud9

```bash
streamlit run contact_console.py --server.port 8080 --server.address=0.0.0.0 
```

#### Configuration screenshot
<img width="1639" alt="console" src="https://github.com/user-attachments/assets/8bde97a3-48b4-433e-8c8b-234823477dcc">
