from flask import Flask, make_response,request,jsonify
import pandas as pd
import io
from sqlalchemy import Column,String,BLOB,Integer,create_engine,DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = Flask(__name__)

CONNECTION_STRING = f'mysql://root:admin@localhost/auth'
CONNECTION = create_engine(CONNECTION_STRING)
Session = sessionmaker(bind=CONNECTION)
session = Session()
Base = declarative_base()

class PdfModel(Base):
    __tablename__ = 'pdfFiles'
    id = Column(Integer,primary_key=True)
    name = Column(String(100))
    pdf_file = Column(BLOB)
    created_at = Column(DATETIME,default=datetime.datetime.utcnow)
        
@app.route('/pdf/<string:id>',methods = ["GET"])
def export_pdf(id):
    pdf_blob = session.query(PdfModel.pdf_file).filter(PdfModel.id==id).first()
    pdf_output = io.BytesIO(pdf_blob[0])
    response = make_response(pdf_output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.pdf"
    response.headers["Content-type"] = "application/pdf"
    return response,200

@app.route('/uploadPdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    print(request.files)
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        pdf_data = file.read()
        
        new_pdf = PdfModel(
            name=file.filename,
            pdf_file=pdf_data
        )
        
        session.add(new_pdf)
        session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'id': new_pdf.id}), 201
    
    return jsonify({'error': 'Invalid file format. Only PDFs are allowed.'}), 400
    

@app.route('/export_xl', methods = ["GET"])
def export_xl():
    res = [{
        "name":"Jabbar",
        "age":20
        }
        ,{
        "name":"OK",
        "age":25
    }]
    df = pd.DataFrame(res)
    out_put = io.BytesIO()
    writer = pd.ExcelWriter(out_put,engine='xlsxwriter')
    df.to_excel(excel_writer=writer,index=False,sheet_name='Jabbar')
    writer.close()
    out_put.seek(0)
    response = make_response(out_put.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    response.headers["Content-type"] = "application/x-xls"
    
    return response, 200

if __name__ == "__main__":
    app.run(port=8088,debug=True)
