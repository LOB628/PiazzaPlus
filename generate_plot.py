import seaborn as sns
import matplotlib.pyplot as plt
from typing import List


def plot_user_activity(user, post: List):
    sns.countplot(x="user_id", data=post)
    plt.title(f"Activity of {user}")
    plt.show()
