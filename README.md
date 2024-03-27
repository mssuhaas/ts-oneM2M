# Thingspeak to oneM2M data

This project fetches data from a ThingSpeak channel, updates the node data, and posts it to an OM2M endpoint periodically.

## Prerequisites

You need to have Python 3.6 or higher installed on your machine. You can verify your Python version by running the following command in your terminal:

```sh
python --version
```
## Install Python Dependencies
Navigate to your project directory and run the following command to install the necessary Python packages:


```sh
pip install -r requirements.txt
```
This command reads the requirements.txt file and installs the packages listed in it.

## Setup

1. Clone this repository to your local machine.

2. Navigate to the project directory.

3. Create a `nodes_info.json` file in the project directory with the following structure:

```json
[
    {
        "node_id": "<node_id>",
        "channel_id": "<channel_id>",
        "api_key": "<api_key>",
        "onem2m_endpoint": "<onem2m_endpoint>"
    },
    ...
]
```

Replace `<node_id>`, `<channel_id>`, `<api_key>`, and `<onem2m_endpoint>` with your actual data. You can add as many nodes as you want.

## Running the Script

To run the script, use the following command in your terminal:

```sh
python main.py
```

The script will fetch and update data for each node in the `nodes_info.json` file every 10 minutes.

## Deployment using service file

### Step 1: Update the Service File

Open the `ts-om2m.service` file and replace `/path/to/your/script/main.py` with the actual path to your Python script and `yourusername` with your actual username.

### Step 2: Copy the Service File

Copy the updated `ts-om2m.service` file to the `/etc/systemd/system/` directory. You can use the `cp` command in the terminal:

```sh
sudo cp ts-om2m.service /etc/systemd/system/
```

### Step 3: Reload Systemd

After adding the new service file, you need to reload the systemd daemon to recognize your service. Run the following command:

```sh
sudo systemctl daemon-reload
```

### Step 4: Start the Service

Start the service by running:

```sh
sudo systemctl start ts-om2m.service
```

### Step 5: Enable the Service

If you want your service to start automatically at boot, you need to enable it:

```sh
sudo systemctl enable ts-om2m.service
```

### Step 6: Check the Service Status

To ensure your service has started successfully, check its status:

```sh
sudo systemctl status ts-om2m.service
```

If the service is running correctly, you should see `active (running)` in the output.

### Step 7: Monitor the Service

You can monitor the service logs using the `journalctl` command:

```sh
sudo journalctl -u ts-om2m.service
```

This command will show you the entire content of the log since the service was started. If you want to follow the log (similar to `tail -f`), you can use the `-f` option:

```sh
sudo journalctl -u ts-om2m.service -f
```

