import subprocess
from gallery.config import settings


# Example usage
if __name__ == "__main__":

    result = subprocess.run(
        ['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
    with open(settings.REQUIREMENTS_INSTALLED_PATH, 'w') as file:
        file.write(result.stdout)

    print(result.stdout)
