#!/usr/bin/env python3
import subprocess
import sys

def check_kafka():
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", "kafka", "-l", "app=kafka"],
            capture_output=True, text=True, check=True
        )
        if "Running" in result.stdout:
            print("✓ Kafka pods running")
            return True
        else:
            print("✗ Kafka pods not ready")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if check_kafka() else 1)
