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
    # Extract custom port if provided
    host = device_params.get('host')
    device_type = device_params.get('device_type')
    
    # Build connection parameters
    conn_params = {
        'device_type': device_type,
        'host': host,
        'username': device_params.get('username'),
        'password': device_params.get('password'),
    }
    
    # Add custom port if specified
    if 'port' in device_params and device_params['port']:
        conn_params['port'] = device_params['port']
        logger.info(f"Using custom port: {device_params['port']}")
    
    # Add secret if provided (for enable mode)
    if 'secret' in device_params and device_params['secret']:
        conn_params['secret'] = device_params['secret']
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Connecting to {host}:{conn_params.get('port', 22)} (attempt {attempt}/{retries})")
            connection = ConnectHandler(**conn_params)
            
            # Enter enable mode if secret provided
            if 'secret' in conn_params:
                connection.enable()
                
            logger.info(f"Successfully connected to {host}")
            return connection
            
        except NetmikoAuthenticationException as auth_err:
            logger.error(f"Authentication failed for {host}: {auth_err}")
            return None  # No retry for bad credentials
            
        except (NetmikoTimeoutException, Exception) as e:
            logger.warning(f"Connection failed for {host}: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All {retries} attempts failed for {host}")
                return None
    
    return None
