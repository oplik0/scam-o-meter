import requests
from datetime import datetime

class CheckKRS:
    def __init__ (self, number):
        self.scam = 0 #miernik - im większa liczba, tym większe prawdopodobieństwo scamu
        self.flags = dict(dict.fromkeys(["www", "email", "address", "country", "pkd_full", "pkd", "relations", "status", "registration_date", "assets", "court", "management", "existance", "connection_error"], False)) #flagi które zostaną przełączone gdy w danych KRS znajdzie się coś wskazującego na scam. Praktycznie u każdej firmy przełączy się część, dlatego dopiero więskza ilość będzie wskazywała na problemy z firmą
        self.date=0
        self.number = number
        self.address = ""
        self.fetch_data()
    def fetch_data (self):
        try:
            self.r = requests.get("https://api.transparentdata.pl/7iIwa75/getKrsData?number={}".format(self.number), auth=("MEkysnS", "sM7Y2fLi")) #pobranie danych z api
            self.krs_data = self.r.json()['data'] #zebranie danych do zmiennej
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout): #na wypadek błędu połączenia...
            for i in range(3):
                try:
                    self.r = requests.get("gttps://api.transparentdata.pl/7iIwa75/getKrsData?number={}".format(self.number), auth=("MEkysnS", "sM7Y2fLi"))
                    self.krs_data = self.r.json()['data']
                    break
                except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
                    if i==2:
                        self.flags["connection_error"] = True
                        return (self.flags, 100, 0, 0)
        if self.krs_data == []: #jeśli numer nie jest właściwy/nie ma firmy o tym numerze, uznaje się firmę za nieistniejącą
            self.scam = 100
            self.flags["existance"] = True
            return self.flags

    def read_details(self):
        if self.krs_data["www"].replace("-", "") == "": #sprawdzenie, czy firma ma wpisaną stronę internetową
            self.scam+=5
            self.flags["www"] = True

        if self.krs_data["email"].replace("-", "") == "": #sprawdzenie, czy firma ma wpisany kontaktory adres email
            self.scam+=5
            self.flags["email"] = True

        if self.krs_data["oznaczenie_sadu"].replace("-", "") == "": #sprawdzenie, czy firma ma oznaczenie sądu
            self.scam+=10
            self.flags["court"] = True

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

        if self.krs_data["kraj"] != "POLSKA": #sprawdzenie, czy firma ma swoją siedzibę w Polsce. Zagraniczna raczej nie jest pożądana.
            self.scam += 30 
            self.flags["country"] = True
        
        if self.krs_data["kapital"] == "5000.00": #firma mająca jedynie minimalny kapitał wymagany do rejestracji jest jednak podejrzana
            self.scam+=10
            self.flags["assets"] = True

        if self.read_date(): #sprawdzenie "świerzości" firmy - firma mająca mniej niż kwartał (lub nawet nieco więcej) jest podejrzana
            self.scam+=10
            self.flags["registration_date"] = True
        
        if self.read_relations(): #sprawdzanie powiązań KRS - w szczególności wspólników i zarządu
            self.scam+=30
            self.flags["relations"] = True
        
        if self.read_address(): #sprawdzenie, czy adres odpowiada któremuś z zebranych w pliku tekstowym biur wirtualnych
            self.scam+=15
            self.flags["address"] = True
        if self.scam>=100:
            self.scam = 99
        return self.flags, self.scam, self.date, self.address

    def read_date(self):
        registration_date = self.krs_data["data_utworzenia"]
        date_now = datetime.now().isoformat()[:10]
        if registration_date[:4] is date_now[:4]:
            if int(date_now[5:7])-int(registration_date[5:7])<=4:
                self.date = int(date_now[5:7])-int(registration_date[5:7])  
                return True
            
        return False

    def read_relations(self):
        pesel = False
        for relation in self.krs_data["krs_relations"]:
            if relation["ident_type"] == "pesel": 
                pesel = True
            if relation["ident_type"] in ("name", "pesel"):
                try:
                    with open("czarna_lista_przedsiebiorcow.txt", 'r') as blacklist_file: #sprawdzenie pliku z czarną listą imion i nazwisk - nazwiska na niej już były powiązane w przeszłości ze scamem
                        blacklist = [line.strip() for line in blacklist_file]
                    if "{} {}".format(relation["name"], relation["last_name"]) in blacklist:
                        self.scam+=80
                        self.flags["management"] = True
                except Exception as e:
                    print(e)
                    
        if pesel: #brak osoby z podanym numerem pesel w relacjach sugeruje, że coś jest nie tak...
            return False
        else:
            return True
    
    def read_address(self):
        self.address = str(self.krs_data["adres"])+' '+str(self.krs_data["numer"])
        try:
            with open("./lista_wirtualnych_biur.txt", 'r') as blacklist_file: #sprawdzenie pliku z listą wirtualnych biur
                blacklist = [line.strip() for line in blacklist_file]
            if self.address[4:].upper() in blacklist:
                return True
        except:
            return False
        
if __name__ == '__main__':
    Check = CheckKRS(input("wpisz numer KRS/NIP/REGON: "))
    flags, scam, date, address = Check.read_details()
    print("prawdopodobieństwo scamu:", scam)
    if flags["registration_date"]:
        print("czas od założenia firmy: {} miesięcy".format(date))
    print("adres firmy:", address)
    print("flagi:", flags)

