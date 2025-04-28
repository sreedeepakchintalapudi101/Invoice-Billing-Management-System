document.getElementById("login-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username_or_email = document.getElementById("username_or_email").value;
  console.log("Username (or) email is ", username_or_email);
  const password = document.getElementById("password").value;
  console.log("Password is", password);

  try {
    const response = await fetch("http://localhost:8081/login_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: username_or_email, password: password })
    });

    const data = await response.json(); // this is your result object

    if (data.flag) {
      document.getElementById("loginResponse").innerText = data.message;
      document.getElementById("otp-section").style.display = "block";
      localStorage.setItem("login_email", username_or_email);
    } 
    else {
      document.getElementById("loginResponse").innerText = data.message;
    }
  } catch (error) {
    console.log("Error:", error);
    document.getElementById("loginResponse").innerText = "Something went wrong. Please try again.";
  }

});

async function validateOTP() {
  const otp = document.getElementById("otp_input").value;
  const username_or_email = document.getElementById("username_or_email").value;

  if (!otp || !username_or_email) {
    alert("Please enter the OTP!");
    return;
  }

  try {
    const response = await fetch("http://localhost:8081/validate_otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: username_or_email, otp: otp })
    });

    const result = await response.json();

    if (result.flag === "success") {
      document.getElementById("loginResponse").innerText = "OTP Verified Successfully!";
      setTimeout(() =>  {
        window.location.href = "/templates/dashboard.html"
      } 
      )
      // Optional: Redirect or load a new page
    } else if (result.flag === "expired") {
      document.getElementById("loginResponse").innerText = "OTP Expired! Please click on resend to get new OTP.";
      document.getElementById("otp_input").value = "";
    } else {
      document.getElementById("loginResponse").innerText = "Invalid OTP! Please try again.";
      document.getElementById("otp_input").value = "";
    }
  } catch (error) {
    document.getElementById("loginResponse").innerText = "Something went wrong. Please try again.";
  }
}
