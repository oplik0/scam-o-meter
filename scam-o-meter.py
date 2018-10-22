from flask import Flask, jsonify, render_template, request
from KRS import KRS
app = Flask(__name__)

@app.route("/number", methods=["post"])
def number():
    nr = str(request.values.get('nr'))
    if len(str(nr))<7:
        return jsonify({"scam":0, "www":"", "email":"", "address":"", "country":"", "pkd_full":"", "relations":"", "status":"", "registration_date":"", "assets":"", "court":"", "management":"", "existance":"", "pkd":"", "nr":nr})
    
    getKRS = KRS.CheckKRS(nr)
    flags, scam, date, registration_address = getKRS.read_details()
    www=email=address=country=pkd_full=relations=status=registration_date=assets=court=management=existance=pkd=""
    if flags["www"]:
        www = "Firma nie wpisała swojej strony do KRS"
    if flags["email"]:
        email="Firma nie wpisała swojego adresu email do KRS"
    if flags["address"]:
        address = "Adres firmy ({}) wskazuje na budynek w których wynajmuje się biura wirtualne, co oznacza, że jest tam firma która wynajmuje to samo miejsce dla wielu innych firm by mogły się tam zarejestrować i tylko ona zna ich prawdziwy adres".format(registration_address)
    if flags["country"]:
        country = "Firma ma siedzibę poza Polską"
    if flags["pkd_full"]:
        pkd_full="Firma ma tylko jeden pkd - profil klasyfikacji działalności. To wskazuje na to, że zajmuje się tylko jedną kategorią działalności, co jest rzadkie dla normalnych firm. Zwykle nawet sklepy internetowe mają w tym miejscu poza sprzedażą detaliczną w internecie"
    if flags["relations"]:
        relations = "Żadna osoba związana z firmą nie podała w KRS swojego numeru PESEL, więc są znacznie bardziej anonimowi"
    if flags["status"]:
        status="Firma nie działa aktywnie!"
    if flags["registration_date"]:
        registration_date = "Firma została zarejestrowana tylko {} miesięcy temu. Nie jest to coś wyjątkowo alarmującego, ale zwykle firmy zajmujące się oszustwami nie działają długo, w przeciwieństwie do prawdziwych przedsiębiorstw".format(date)
    if flags["assets"]:
        assets = "Kapitał firmy jest minimalnym kapitałem wymaganym do założenia spółki."
    if flags["court"]:
        court = "W KRS nie ma oznaczenia sądu rejestrowego w którym przechowywane są akta firmy"
    if flags["management"]:
        management = "Jedna z osób związanych z firmą już w przeszłości była powiązana z oszustwem - UWAŻAJ!"
    if flags["existance"]:
        existance = "Sprawdź poprawność podanego numeru. Jeśli jest prawidłowy, UWAŻAJ! Firma nie ma wpisu w KRS, co najpewniej oznacza, że nie istnieje"
    if flags["pkd"]:
        pkd = "PKD firmy wskazuje na sklep internetowy, albo call center - najczęstsze profile oszustów. Nie zwracaj jednak na specjalnej uwagi jeśli firma ma być sklepem/call center"
    return jsonify({"scam":scam, "www":www, "email":email, "address":address, "country":country, "pkd_full":pkd_full, "relations":relations, "status":status, "registration_date":registration_date, "assets":assets, "court":court, "management":management, "existance":existance, "pkd":pkd}), 200
@app.route('/')
def index():
    return render_template('index.html')