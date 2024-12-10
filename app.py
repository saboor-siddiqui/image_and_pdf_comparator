from flask import Flask, request, render_template, flash, redirect
from PIL import Image
from io import BytesIO
import os
import numpy as np
import base64
from image_comparator import ImageComparator
from multiple_image_comparator import MultipleImageComparator

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
multiple_comparator = MultipleImageComparator(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Get files from request
            file1 = request.files['file1']
            file2 = request.files['file2']
            
            # Read files into memory using PIL
            image1 = Image.open(BytesIO(file1.read()))
            image2 = Image.open(BytesIO(file2.read()))
            
            # Convert to RGB mode if necessary
            if image1.mode != 'RGB':
                image1 = image1.convert('RGB')
            if image2.mode != 'RGB':
                image2 = image2.convert('RGB')
            
            # Convert to numpy arrays
            image1_np = np.array(image1)
            image2_np = np.array(image2)
            
            # Compare images and get result
            output_image = single_comparator.compare_images_in_memory(image1_np, image2_np)
            
            # Convert output image to bytes for display
            output_buffer = BytesIO()
            Image.fromarray(output_image).save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            # Return result template with image data
            return render_template('result.html', output_image=output_buffer)
            
        except Exception as e:
            flash(str(e))
            print(f"Error during comparison: {str(e)}")  # Debug logging
            return redirect(request.url)
            
    return render_template('index.html')

@app.route('/compare_multiple', methods=['POST'])
def compare_multiple():
    try:
        # Use multiple image comparator
        parent_file = request.files['master_file']
        child_files = request.files.getlist('child_files')
        
        if len(child_files) < 5:
            flash("Please select at least 5 files to compare")
            return redirect(request.url)
            
        # Read parent file into memory
        parent_image = Image.open(BytesIO(parent_file.read()))
        parent_image_np = np.array(parent_image)
        
        child_images = []
        for child_file in child_files:
            # Read child files into memory
            child_image = Image.open(BytesIO(child_file.read()))
            child_image_np = np.array(child_image)
            child_images.append(child_image_np)
        
        results = multiple_comparator.compare_multiple(parent_image_np, child_images)
        
        # Convert output images to in-memory files
        output_buffers = []
        for result in results.values():
            output_buffer = BytesIO()
            result.output_image.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            output_buffers.append(output_buffer)
        
        return render_template('multiple_results.html', results=results, parent_image=parent_file.filename)
                             
    except Exception as e:
        flash(str(e))
        print(f"Error during multiple comparison: {str(e)}")
        return redirect(request.url)

@app.route('/convert_html', methods=['POST'])
def convert_html():
    try:
        html_file = request.files['html_file']
        html_file_path = BytesIO(html_file.read())

        output_image_path = BytesIO()
        single_comparator.html_to_image(html_file_path, output_image_path)
        output_image_path.seek(0)

        return render_template('result.html', output_image=output_image_path)
    except Exception as e:
        flash(str(e))
        print(f"Error during HTML conversion: {str(e)}")
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)