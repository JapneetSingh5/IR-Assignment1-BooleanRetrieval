from bs4 import BeautifulSoup

soup = BeautifulSoup(open('../tipster-ap-frac/ap880212', 'r'), 'html.parser')
print(soup)