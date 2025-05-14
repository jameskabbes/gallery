import subprocess
import config

# Example usage
if __name__ == "__main__":

    result = subprocess.run(
        ['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
    with open(config.REQUIREMENTS_INSTALLED_PATH, 'w') as file:
        file.write(result.stdout)

    print(result.stdout)
