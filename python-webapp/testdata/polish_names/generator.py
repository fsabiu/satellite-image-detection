from random import choice

from testdata.polish_names import names


def generate_people(number=1, gender='M'):
    """
    Function for generating people
    
    :param int number: Number of names to generate
    :param str recipient: Gender of names to generate (M, F, X)
    :return: list of names
    :rtype: list
    """

    if gender == 'M':
        list_first_names = names.FIRST_NAMES_M
        list_second_names = names.LAST_NAMES_M
    elif gender == 'F':
        list_first_names = names.FIRST_NAMES_F
        list_second_names = names.LAST_NAMES_F
    else:
        return "Provide valid gender type!"

    names_list = []
    for e in range(number):
        temp_name = choice(list_first_names)
        temp_surname = choice(list_second_names)
        temp_person = f"{temp_name} {temp_surname}"

        names_list.append(temp_person)

    return names_list