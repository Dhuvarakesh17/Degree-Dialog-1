import API_BASE_URL from '../config';

fetch(`${API_BASE_URL}api/endpoint`)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));




const API_BASE_URL = "https://your-backend.onrender.com/"; // Backend URL

export default API_BASE_URL;
