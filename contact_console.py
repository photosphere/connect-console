import os
import streamlit as st
import pandas as pd
import boto3
import json
import time
import threading

# Initialize Boto3 client
connect_client = boto3.client("connect")

connect_instance_id = ''
queues_selected = ''

queues_file_name = 'queues.csv'
selected_queues_file_name = 'selected_queues.csv'
queues_edited_data = pd.DataFrame()

flows_file_name = 'flows.csv'
selected_flows_file_name = 'selected_flows.csv'
flows_edited_data = pd.DataFrame()


def get_selected_queues(queues):
    """
    Retrieve a list of selected queue ARNs from the provided queues DataFrame.

    Args:
        queues (pd.DataFrame): DataFrame containing queue information.

    Returns:
        list: List of selected queue ARNs.
    """
    data = [row['Arn'] for index, row in queues.iterrows()]
    return data


def load_configuration(connect_instance_id):
    """
    Load the Connect instance configuration and related data.

    Args:
        connect_instance_id (str): Connect instance ID.

    Returns:
        bool: True if the configuration was loaded successfully, False otherwise.
    """
    try:
        res = connect_client.describe_instance(InstanceId=connect_instance_id)
        connect_filtered = {k: v for k, v in res['Instance'].items() if k in [
            'Id', 'Arn']}
        with open('connect.json', 'w') as f:
            json.dump(connect_filtered, f)

        st.success("Configuration loaded!")
        return True
    except Exception as e:
        return False


def load_queues(connect_instance_id):
    try:
        # Load queues
        res = connect_client.list_queues(
            InstanceId=connect_instance_id, QueueTypes=['STANDARD'])
        df = pd.DataFrame(res['QueueSummaryList'])
        if len(df) > 0:
            df.to_csv(queues_file_name, index=False)

        return True
    except Exception as e:
        return False


def delete_queues(connect_instance_id, edited_data):
    try:
        if os.path.exists(queues_file_name):
            df = pd.read_csv(queues_file_name)

            selected_rows = edited_data[edited_data['Select']].index.tolist()
            df.loc[selected_rows].to_csv(
                selected_queues_file_name, index=False)

            if os.path.exists(selected_queues_file_name):
                selected_df = pd.read_csv(selected_queues_file_name)

                for index, row in selected_df.iterrows():
                    res = connect_client.delete_queue(
                        InstanceId=connect_instance_id, QueueId=row['Id'])
        return True
    except Exception as e:
        return False


def analyse_queues(connect_instance_id, edited_data):
    try:
        if os.path.exists(queues_file_name):
            df = pd.read_csv(queues_file_name)

            selected_rows = edited_data[edited_data['Select']].index.tolist()
            df.loc[selected_rows].to_csv(
                selected_queues_file_name, index=False)

            if os.path.exists(selected_queues_file_name):
                selected_df = pd.read_csv(selected_queues_file_name)

                for index, row in selected_df.iterrows():
                    res = connect_client.list_queue_quick_connects(
                        InstanceId=connect_instance_id, QueueId=row['Id'])
                    st.dataframe(res['QuickConnectSummaryList'])
        return True
    except Exception as e:
        return False


def delete_flows(connect_instance_id, edited_data):
    try:
        if os.path.exists(flows_file_name):
            df = pd.read_csv(flows_file_name)

        selected_rows = edited_data[edited_data['Select']].index.tolist()
        df.loc[selected_rows].to_csv(selected_flows_file_name, index=False)
        if os.path.exists(selected_flows_file_name):
            selected_df = pd.read_csv(selected_flows_file_name)

            for index, row in selected_df.iterrows():
                res = connect_client.delete_contact_flow(
                    InstanceId=connect_instance_id, ContactFlowId=row['Id'])

        return True
    except Exception as e:
        return False


def load_flows(connect_instance_id):
    # List active flows of selected types
    try:
        contact_flow_types = ["CONTACT_FLOW", "AGENT_WHISPER", "AGENT_TRANSFER",
                              "AGENT_HOLD", "CUSTOMER_QUEUE", "QUEUE_TRANSFER", "OUTBOUND_WHISPER"]
        res = connect_client.list_contact_flows(InstanceId=connect_instance_id)
        df = pd.DataFrame(res['ContactFlowSummaryList'])
        df = df[df['ContactFlowState'] == 'ACTIVE']
        df = df[df['ContactFlowType'].str.upper().isin(
            contact_flow_types)]
        if not df.empty:
            df.to_csv(flows_file_name, index=False)

        return True
    except Exception as e:
        st.error('Load Flows Failed')
        return False


def get_edited_data(file):
    if os.path.exists(file):
        df = pd.read_csv(file)
        df.insert(0, 'Select', False)
        df_edited_data = st.data_editor(df)
        return df_edited_data
    return pd.DataFrame()


def clear():
    try:
        if os.path.exists(queues_file_name):
            os.remove(queues_file_name)
        if os.path.exists(selected_queues_file_name):
            os.remove(selected_queues_file_name)
        if os.path.exists(flows_file_name):
            os.remove(flows_file_name)
        if os.path.exists(selected_flows_file_name):
            os.remove(selected_flows_file_name)
        return True
    except Exception as e:
        return False


def display(success, successtext, failtext):
    if (success):
        st.success(successtext)
    else:
        st.error(failtext)


def main():
    st.set_page_config(
        page_title="Amazon Connect Admin Console!", layout="wide")

    # App title
    st.header(f"Amazon Connect Admin Console!")

    if os.path.exists('connect.json'):
        with open('connect.json') as f:
            connect_data = json.load(f)
            connect_instance_id = connect_data['Id']

    # Connect configuration

    connect_instance_id = st.text_input(
        'Connect Instance Id', value=connect_instance_id)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
    with col1:
        load_queue_button = st.button('Load Queue')
    with col2:
        load_flow_button = st.button('Load Flow')
    with col3:
        clear_button = st.button('Clear', type='primary')

        # Clear
    if (clear_button):
        display(clear(), 'Data Cleared', 'Clear Data Failed')

    # Load queue
    if load_queue_button:
        with st.spinner('Loading...'):
            display(load_queues(connect_instance_id),
                    'Queues Loaded', 'Load Queues Failed')

    queues_edited_data = get_edited_data(queues_file_name)

    if os.path.exists(queues_file_name):
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            delete_queue_button = st.button('Delete Queue')
        with col2:
            analyse_queue_button = st.button('Analyse Queue')

        if (delete_queue_button):
            display(delete_queues(connect_instance_id, queues_edited_data),
                    'Queues Deleted', 'Delete Queues Failed')

        if (analyse_queue_button):
            analyse_queues(connect_instance_id, queues_edited_data)

            # Load flow
    if load_flow_button:
        with st.spinner('Loading...'):
            display(load_flows(connect_instance_id),
                    'Flows Loaded', 'Load Flows Failed')

    flows_edited_data = get_edited_data(flows_file_name)

    if os.path.exists(flows_file_name):
        flow_queue_button = st.button('Delete Flow')
        if (flow_queue_button):
            display(delete_flows(connect_instance_id, flows_edited_data),
                    'Flows Deleted', 'Delete Flows Failed')


if __name__ == "__main__":
    main()
