from flask import Flask

app = Flask(__name__)


@app.route("/meteolog.cgi")
def meteolog():
    return """
        <logger>
            <RAIN date="20231121115139" id="rain0" rate="0.0" total="367.5" delta="0.0" lowbat="0" />
            <TH date="20231121115202" id="th0" temp="10.0" hum="87" dew="7.9" lowbat="0" />
            <WIND date="20231121115204" id="wind0" dir="158" gust="0.0" wind="0.0" chill="10.0" lowbat="0" />
            <THB date="20231121115200" id="thb0" temp="21.4" hum="34" dew="4.9" press="1000.0" seapress="1019.0" fc="2" lowbat="0" />
        </logger>
    """


if __name__ == "__main__":
    app.run()
