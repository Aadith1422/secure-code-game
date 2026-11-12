
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "regexp"
)

func isValidEmail(email string) bool {
    emailPattern := `^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$`
    match, err := regexp.MatchString(emailPattern, email)
    if err != nil {
        return false
    }
    return match
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    // Request data is now local to each request.
    var reqBody struct {
        Email    string `json:"email"`
        Password string `json:"password"`
    }

    testFakeMockUsers := map[string]string{
        "user1@example.com": "password12345",
        "user2@example.com": "B7rx9OkWVdx13$QF6Imq",
        "user3@example.com": "hoxnNT4g&ER0&9Nz0pLO",
        "user4@example.com": "Log4Fun",
    }

    if r.Method != http.MethodPost {
        http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
        return
    }

    decode := json.NewDecoder(r.Body)
    decode.DisallowUnknownFields()

    if err := decode.Decode(&reqBody); err != nil {
        http.Error(w, "Cannot decode body", http.StatusBadRequest)
        return
    }

    email := reqBody.Email
    password := reqBody.Password

    if !isValidEmail(email) {
        log.Printf("Invalid email format")
        http.Error(w, "Invalid email format", http.StatusBadRequest)
        return
    }

    storedPassword, ok := testFakeMockUsers[email]
    if !ok || password != storedPassword {
        http.Error(w, "Invalid Email or Password", http.StatusUnauthorized)
        return
    }

    // Never log passwords.
    log.Print("Successful login request")
    w.WriteHeader(http.StatusOK)
}

func main() {
    http.HandleFunc("/login", loginHandler)
    log.Print("Server started. Listening on :8080")

    err := http.ListenAndServe(":8080", nil)
    if err != nil {
        log.Fatalf("HTTP server ListenAndServe: %q", err)
    }
}
