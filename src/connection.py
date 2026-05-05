import logging
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import time

logger = logging.getLogger(__name__)

def connect_device(device_params, retries=2, delay=5):
    """
    Establish SSH connection to network device using Netmiko with retry logic.
    
    Args:
        device_params (dict): Netmiko connection dict (host, username, password, device_type)
        retries (int): Number of retry attempts
        delay (int): Seconds to wait between retries
    
    Returns:
        netmiko.ConnectHandler: Connection object or None if all retries fail
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Connecting to {device_params['host']} (attempt {attempt}/{retries})")
            connection = ConnectHandler(**device_params)
            # Send enable command if secret provided
            if 'secret' in device_params and device_params['secret']:
                connection.enable()
            logger.info(f"Successfully connected to {device_params['host']}")
            return connection
        except NetmikoAuthenticationException as auth_err:
            logger.error(f"Authentication failed for {device_params['host']}: {auth_err}")
            return None  # No retry for bad credentials
        except (NetmikoTimeoutException, Exception) as e:
            logger.warning(f"Connection failed for {device_params['host']}: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All {retries} attempts failed for {device_params['host']}")
                return None
    return None