document.getElementById('file-upload').onchange = function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const imgElement = document.getElementById('preview');
        imgElement.src = e.target.result;
        imgElement.style.display = 'block';
    };
    
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://127.0.0.1:5000/up_img', {
        method: 'POST',
        body: formData
    }).then(response => response.json()).then(data => {
        if (data.error){
            document.getElementById('ocr-result').innerText = "Error: " + data.error;
        }
        else{
        document.getElementById('ocr-result').innerText = "License Plate: " + data.txt;
        }
    }).catch(error => console.error('Error:', error));
};
