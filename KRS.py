import requests
import time

class CheckKRS:
    def __init__ (self, number):
        self.scam = 0 #miernik - im większa liczba, tym większe prawdopodobieństwo scamu
        self.flags = dict(dict.fromkeys(["www", "email", "adress", "country", "pkd_full", "relations", "status", "registration_date", "assets", "court", "management", "existance", "connection_error"], False)) #flagi które zostaną przełączone gdy w danych KRS znajdzie się coś wskazującego na scam. Praktycznie u każdej firmy przełączy się część, dlatego dopiero więskza ilość będzie wskazywała na problemy z firmą
        self.number = number
        self.fetch_data()
        self.read_details()
    def fetch_data (self):
        try:
            self.r = requests.get("https://api.transparentdata.pl/7iIwa75/getKrsData?number={}".format(self.number), auth=("MEkysnS", "sM7Y2fLi")) #pobranie danych z api
            self.krs_data = self.r.json()['data'] #zebranie danych do zmiennej
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout): #na wypadek błędu połączenia...
            return ({"connection_error":True}, 100)

        if self.krs_data == []: #jeśli numer nie jest właściwy/nie ma firmy o tym numerze, uznaje się firmę za nieistniejącą
            self.scam = 100
            self.flags["nonexistant"] = True
            return self.flags

    def read_details(self):
        if self.krs_data['www'].replace("-", "") == "": #sprawdzenie, czy firma ma wpisaną stronę internetową
            self.scam+=5
            self.flags["www"] = True

        if self.krs_data['email'].replace("-", "") == "": #sprawdzenie, czy firma ma wpisany kontaktory adres email
            self.scam+=5
            self.flags["email"] = True

        if self.krs_data["pkd_pelne"].replace("-", "") == "": #sprawdzanie, czy firma ma wpisany więcej niż 1 pkd, co jest częste dla prawdziwych firm, ale rzadkie dla firm powstałych na potrzeby jednego scamu. Oczywiście zdarzają się wyjątki w obie strony.
            self.scam+=15
            self.flags["pkd_full"] = True

        if self.krs_data['pkd_glowne'] in ("8220Z", "4791Z"): #sprawdzenie pkd głównego - 8220Z oznacza call center, a 4791Z sklep internetowy. Są to chyba 2 najpopularniejsze sposoby działalności firm zajmujących się scamami w internecie
            self.scam += 10
            self.flags["pkd"] = True
            if self.flags["pkd_full"]:
                self.scam +=10 #sklep internetowy/call center jako jedyny profil działalności jeszcze bardziej zwiększa szanse na scam

        if self.krs_data["status_podmiotu"] != "aktywna": #sprawdzanie statusu firmy - jeśli jest inny niż "aktywna"
            self.scam+=80
            self.flags["status"] = True

        if self.krs_data['kraj'] != "POLSKA": #sprawdzenie, czy firma ma swoją siedzibę w Polsce. Zagraniczna raczej nie jest pożądana.
            self.scam += 30 
            self.flags["country"] = True
        
        if self.krs_data["kapital"] == "5000.00": #firma mająca jedynie minimalny kapitał wymagany do rejestracji jest jednak podejrzana
            self.scam+=10
            self.flags["assets"] = True
        

        
        
if __name__ == '__main__':
    CheckKRS(int(input('wpisz numer KRS/NIP/REGON')))
