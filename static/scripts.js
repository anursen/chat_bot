function submitData() {
    const userID = document.getElementById("userID").value;
    const systemMessage = document.getElementById("systemMessage").value;
    const llm_model = document.getElementById("llm_model").value;
    const chatMessage = document.getElementById("chatInput").value;
    const behaviour = document.getElementById("behaviour").value;
    const pdfFiles = document.getElementById("fileUpload").files;

    const formData = new FormData();
    formData.append("userID", userID);  // New field for user ID
    formData.append("systemMessage", systemMessage);
    formData.append("chatMessage", chatMessage);
    formData.append("llm_model", llm_model);
    formData.append("behaviour", behaviour);

    // Append each file to form data
    for (let i = 0; i < pdfFiles.length; i++) {
        formData.append("fileUpload", pdfFiles[i]);
    }

    // Display the human message in the message log with userID
    appendMessage(chatMessage, true); // Passing true since this is a user message

    fetch("/submit", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display the AI response in the message log
        appendMessage(data.response, false); // Passing false for AI response

        // Clear the input field after submitting
        document.getElementById("chatInput").value = "";

        // Check the length of the message log and disable the tone selection if needed
        const messageLog = document.getElementById("messageLog");
        if (messageLog.childElementCount > 1) {
            document.getElementById("systemMessage").disabled = true;
            document.getElementById("llm_model").disabled = true;
            document.getElementById("behaviour").disabled = true;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function appendMessage(message, isUser) {
    const messageLog = document.getElementById("messageLog");
    let userID = document.getElementById("userID").value;

    // Determine if the message is from the user or AI
    if (isUser) {
        message = userID + ": " + message; // Show userID instead of "You"
    } else {
        message = "AI: " + message;
    }

    // Create a new message element
    const messageElement = document.createElement('div');
    messageElement.textContent = message;

    // Append the new message to the message log
    messageLog.appendChild(messageElement);

    // Scroll to the top of the message log to show the latest message
    messageLog.scrollTop = messageLog.scrollHeight;
}

const fileUploadInput = document.getElementById('fileUpload');
const fileList = document.getElementById('fileList');
const behaviourSelect = document.getElementById('behaviour');
const submitButton = document.getElementById('submitBtn');

// Function to check if the submit button should be enabled or disabled
function checkSubmitButtonState() {
    if (behaviourSelect.value === 'chatbot_rag_qa' && fileUploadInput.files.length === 0) {
        submitButton.disabled = true; // Disable the submit button
    } else {
        submitButton.disabled = false; // Enable the submit button
    }
}

// Event listener for behavior selection
behaviourSelect.addEventListener("change", function() {
    if (behaviourSelect.value === 'chatbot_rag_qa') {
        fileUploadInput.disabled = false; // Enable the file upload input
    } else {
        fileUploadInput.disabled = true; // Disable the file upload input
        fileUploadInput.value = ""; // Clear the file input value
        fileList.innerHTML = ""; // Clear the file list
    }
    checkSubmitButtonState(); // Check the state of the submit button
});

// Event listener for file upload
fileUploadInput.addEventListener('change', function(event) {
    const files = event.target.files;
    fileList.innerHTML = '';  // Clear previous files

    Array.from(files).forEach(file => {
        const listItem = document.createElement('li');
        const fileName = document.createElement('span');
        fileName.textContent = file.name;

        const cancelIcon = document.createElement('span');
        cancelIcon.textContent = '❌'; // Cancel icon
        cancelIcon.className = 'cancel-icon';
        cancelIcon.onclick = () => {
            listItem.remove();  // Remove the file from the list
            checkSubmitButtonState(); // Re-check the submit button state after removing a file
        };

        listItem.appendChild(fileName);
        listItem.appendChild(cancelIcon);
        fileList.appendChild(listItem);
    });

    checkSubmitButtonState(); // Check the state of the submit button
});
