import json
import cv2
import logging
import uuid
import numpy as np
import base64
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageChops, ImageEnhance
from flask import Flask, jsonify, request
app = Flask(__name__)

employees = [
 { 'id': 1, 'name': 'Ashley' },
 { 'id': 2, 'name': 'Kate' },
 { 'id': 3, 'name': 'Joe' }
]


nextEmployeeId = 4
3
@app.route('/employees', methods=['GET'])
def get_employees():
    return jsonify(employees)

@app.route('/employees/<int:id>', methods=['GET'])
def get_employee_by_id(id: int):
    employee = get_employee(id)
    if employee is None:
        return jsonify({ 'error': 'Employee does not exist'}), 404
    return jsonify(employee)

def get_employee(id):
    return next((e for e in employees if e['id'] == id), None)

def employee_is_valid(employee):
    
    for key in employee.keys():
        if key != 'name':
            return False
        return True

@app.route('/employees', methods=['POST'])
def create_employee():
    global nextEmployeeId
    app.logger.info(request.data)
    employee = json.loads(request.data)
    if not employee_is_valid(employee):
        return jsonify({ 'error': 'Invalid employee properties.' }), 400

    employee['id'] = nextEmployeeId
    nextEmployeeId += 1
    employees.append(employee)

    return '', 201, { 'location': f'/employees/{employee["id"]}' }

@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id: int):
    employee = get_employee(id)
    if employee is None:
        return jsonify({ 'error': 'Employee does not exist.' }), 404

    updated_employee = json.loads(request.data)
    if not employee_is_valid(updated_employee):
        return jsonify({ 'error': 'Invalid employee properties.' }), 400

    employee.update(updated_employee)

    return jsonify(employee)

@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id: int):
    global employees
    employee = get_employee(id)
    if employee is None:
        return jsonify({ 'error': 'Employee does not exist.' }), 404

    employees = [e for e in employees if e['id'] != id]
    return jsonify(employee), 200

#image processing functions==============================================================
@app.route('/imagesapi', methods=['POST'])
def analyze_imagehistogram():
    # return request.data.decode()
    imagehistory = detect_histogram_anomaly64(request.data.decode())
    return imagehistory

@app.route('/imagesapi', methods=['GET'])
def get_images():
    return jsonify(employees)

def detect_histogram_anomaly(image_path):
    img = cv2.imread(image_path, 0)  # grayscale
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    # print(hist[hist.__len__()-1])
    # print(max(hist))
    # print(min(hist))
    
    plt.plot(hist)
    plt.title('Pixel Intensity Histogram')
    plt.show()
    
def detect_histogram_anomaly64(image_base64):
    decodedimage= base64.decodebytes(image_base64.encode())
    imageid = str(uuid.uuid4())+".jpg"
    with open(imageid, "wb") as f:
        f.write(decodedimage)
    img = cv2.imread(imageid, 0)  # grayscale
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])

    try:
        os.remove(imageid)
    except OSError:
        pass

    return hist.tolist()
    # print(hist[hist.__len__()-1])
    # print(max(hist))
    # print(min(hist))
    
    # plt.plot(hist)
    # plt.title('Pixel Intensity Histogram')
    # plt.show()

def ela_analysis(image_path):
    original = Image.open(image_path).convert('RGB')
    original.save("resaved.jpg", "JPEG", quality=90)
    resaved = Image.open("resaved.jpg")
    
    diff = ImageChops.difference(original, resaved)
    enhancer = ImageEnhance.Brightness(diff)
    diff = enhancer.enhance(20)
    diff.show()
#=============================================================

 
# if __name__ == '__main__':
app.run(port=8000)