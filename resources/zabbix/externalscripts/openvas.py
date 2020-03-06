import sys
import argparse
from openvas_lib import VulnscanManager, VulnscanException


parser = argparse.ArgumentParser(description='Discover WordPress version with Machine Learning')
parser.add_argument('-i', '--ip', help='IP address to scan', type=str, action="store")
parser.add_argument('-m', '--method', help='Web scan or normal scan', type=str, action="store")
args = parser.parse_args()

if args.ip and args.method:
	try:
		scanner = VulnscanManager("192.168.1.13", "admin", "admin")
		scan_id, target_id = scanner.launch_scan(target = args.ip,
                                         profile = args.method)

	except VulnscanException as e:
		print("Error:")
		print(e)


else:
	sys.exit()
