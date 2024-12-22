from flask import Flask, request, render_template, flash, redirect
from PIL import Image
from io import BytesIO
import os
import numpy as np
import base64
from image_comparator import ImageComparator
from file_processor import FileProcessor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your-secret-key-here'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Add base64 encode filter
@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Create instances of both comparators with upload folder
single_comparator = ImageComparator(app.config['UPLOAD_FOLDER'])
file_processor = FileProcessor(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Handle image comparison
            if 'file1' in request.files and 'file2' in request.files:
                file1 = request.files['file1']
                file2 = request.files['file2']
                
                file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
                file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
                
                file1.save(file1_path)
                file2.save(file2_path)
                
                # Process files to ensure they are images
                image1_path = file_processor.process_file(file1_path)
                image2_path = file_processor.process_file(file2_path)
                
                comparison_result_image = single_comparator.compare_images(image1_path, image2_path)
                
                # Read the comparison result image and convert to base64
                with open(comparison_result_image, "rb") as image_file:
                    output_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                return render_template('result.html', output_image=output_image)
            
            # Handle HTML comparison
            elif 'html_file1' in request.files and 'html_file2' in request.files:
                html_file1 = request.files['html_file1']
                html_file2 = request.files['html_file2']
                
                html_path1 = os.path.join(app.config['UPLOAD_FOLDER'], html_file1.filename)
                html_path2 = os.path.join(app.config['UPLOAD_FOLDER'], html_file2.filename)
                
                html_file1.save(html_path1)
                html_file2.save(html_path2)
                
                image_path1 = file_processor.convert_html_to_image(html_path1)
                image_path2 = file_processor.convert_html_to_image(html_path2)
                
                comparison_result_image = single_comparator.compare_images(image_path1, image_path2)
                
                # Read the comparison result image and convert to base64
                with open(comparison_result_image, "rb") as image_file:
                    output_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                return render_template('result.html', output_image=output_image)
            
            else:
                flash("Please upload the required files.")
                return redirect(request.url)
        
        except Exception as e:
            flash(str(e))
            print(f"Error during comparison: {str(e)}")
            return redirect(request.url)
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)