import requests
import time

class CheckKRS:
    def __init__ (self, number):
        self.scam = 0 #miernik - z założenia ta zmienna ma osiągać wartości od 0 do 100
        self.flags = dict(dict.fromkeys(["www", "email", "adress", "country", "pkd", "relations", "status", "registration_date", "assets", "court", "management", "existance", "connection_error"], False)) #flagi które zostaną przełączone gdy w danych KRS znajdzie się coś wskazującego na scam. Praktycznie u każdej firmy przełączy się część, dlatego dopiero więskza ilość będzie wskazywała na problemy z firmą
        self.number = number
        
    def fetch_data (self):
        try:
            self.r = requests.get("https://api.transparentdata.pl/7iIwa75/getKrsData?number={}".format(self.number), auth=("MEkysnS", "sM7Y2fLi"))
            self.krs_data = self.r.json()['data']
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
            return {"connection_error":True}
        if self.krs_data == []:
            self.flags["nonexistant"] = True
            return self.flags

    def read_contact_details(self):
        if self.krs_data['www'].replace("-", "") == "":
            self.scam+=4
            self.flags["www"] = True
        if self.krs_data['email'].replace("-", "") == "":
            self.scam+=4
            self.flags["email"] = True

if __name__ == '__main__':
    CheckKRS(int(input('wpisz numer KRS/NIP/REGON')))
