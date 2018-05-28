from ..shared import prep_yoy_data

if __name__ == '__main__':
    yoy_data = prep_yoy_data()
    print yoy_data.head()