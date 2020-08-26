use assets
db.createUser(
  {
    user: "alexfrancow",
    pwd: "abc123",
    roles: [
      {
        role: "readWrite",
        db: "assets"
      }
    ]
  }
)
