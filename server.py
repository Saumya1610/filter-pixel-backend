import os
from flask import Flask, jsonify
from flask_cors import CORS 
import piexif

app = Flask(__name__)
CORS(app)

def get_exif_data(file_path):
    try:
        exif_data = piexif.load(file_path)

        # Process byte-like objects to strings
        for key, value in exif_data.items():
            if value is not None and isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, bytes):
                        exif_data[key][k] = v.decode('utf-8', 'ignore')

        width = exif_data['0th'].get(piexif.ImageIFD.ImageWidth, '')
        length = exif_data['0th'].get(piexif.ImageIFD.ImageLength, '')
        size = f'{width} X {length}'
        make = exif_data['0th'].get(piexif.ImageIFD.Make, ''),
        model = exif_data['0th'].get(piexif.ImageIFD.Model, ''),
        camera =  f'{make} {model}'
        data = {
            "file_path": os.path.basename(file_path),
            "lens": exif_data['Exif'].get(piexif.ExifIFD.LensSpecification, ''),
            "capture_time_date": exif_data['0th'].get(piexif.ImageIFD.DateTime, ''),
            "iso_speed": exif_data['Exif'].get(piexif.ExifIFD.ISOSpeed, ''),
            "iso_speed_ratings": exif_data['Exif'].get(piexif.ExifIFD.ISOSpeedRatings, ''),
            "aperture_value": exif_data['Exif'].get(piexif.ExifIFD.ApertureValue, ''),
            "width": width,
            "length": length,
            "size": size,
            "white_balance": exif_data['Exif'].get(piexif.ExifIFD.WhiteBalance, ''),
            "rating": exif_data['Exif'].get(piexif.ImageIFD.Rating, ''),
            "color": exif_data['Exif'].get(piexif.ImageIFD.ColorMap, ''),
            "camera":camera,
            "artist": exif_data['0th'].get(piexif.ImageIFD.Artist, ''),
            "sharpness": exif_data['Exif'].get(piexif.ExifIFD.Sharpness, ''),
            "focal_length": exif_data['Exif'].get(piexif.ExifIFD.FocalLength, ''),
            "brightness_value": exif_data['Exif'].get(piexif.ExifIFD.BrightnessValue, '')
        }
        return data

    except (KeyError, Exception) as e:
        print(f"Error processing {file_path}: {e}")
        return {"file_path": file_path, "error": str(e)}

@app.route('/exif', methods=['GET'])
def exif_data_route():
    assets_dir = os.path.join(app.root_path, 'assets')
    image_paths = [os.path.join(assets_dir, f) for f in os.listdir(assets_dir) if f.lower().endswith(('.nef', '.dng', '.arw', '.pef', '.orf', '.dcr'))]
    exif_results = [get_exif_data(path) for path in image_paths]
    return jsonify(exif_results)

if __name__ == '__main__':
    app.run(debug=True)
