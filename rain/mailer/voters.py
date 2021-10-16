"""Application module to manage voter file management."""

# PIP imports
import pandas as pd

# Library imports
from rain.mailer import Person


def persons(filename):
    """Convert voter email file to list of Person objects.

    Args:
        filename: Name of tsv with voters

    Returns:
        result: List of Person objects

    """
    # Initialize key variables
    result = []
    uniques = {}
    df_ = pd.read_csv(filename, header=0)

    # Convert Nan to None
    df_ = df_.where(pd.notnull(df_), None)

    # Create Person objects
    for _, row in df_.iterrows():
        f_name = row['firstname'].strip() if bool(row['firstname']) else None
        f_name = f_name if bool(f_name) else None

        l_name = row['lastname'].strip() if bool(row['lastname']) else None
        l_name = l_name if bool(l_name) else None

        email = row['email'].strip() if bool(row['email']) else None
        email = email if bool(email) else None

        # Add to dict
        if bool(email) is True:
            uniques[email] = Person(
                firstname=f_name, lastname=l_name, email=email)

    # Create a list of unique tuples
    for _, value in uniques.items():
        result.append(value)

    # Return
    return result
