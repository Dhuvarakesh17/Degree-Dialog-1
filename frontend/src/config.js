import API_BASE_URL from '../config';

fetch(`${API_BASE_URL}api/endpoint`)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));




/**
 * The base URL for the backend API.
 * @type {string}
 */
const API_BASE_URL = "https://degree-dialog-1-1.onrender.com"; // Backend URL

export default API_BASE_URL;
