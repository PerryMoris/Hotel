const form = document.getElementById("mb-4");

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(form);

    fetch("login.php", {
        method: "POST",
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Login successful, redirect or display success message
                console.log("Login successful!");
                // Redirect to dashboard or protected page
                window.location.href = "dashboard.html"; // Replace with your desired URL
            } else {
                // Login failed, display error message
                const errorMessage = document.getElementById('error-message');
                errorMessage.textContent = data.error;
                errorMessage.style.display = 'block';
            }
        })
        .catch(error => {
            console.error("Error:", error);
            // Handle network errors or other issues
            const errorMessage = document.getElementById('error-message');
            errorMessage.textContent = "An error occurred. Please try again later.";
            errorMessage.style.display = 'block';
        });
});
