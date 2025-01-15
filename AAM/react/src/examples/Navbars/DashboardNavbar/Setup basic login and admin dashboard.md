Setup basic login and admin dashboard
user.niyud.co.il (ULM )
  Show the login form/
  On login set cookies and return token to the API the redirect to admin (Will make this dynamic once setup)

admin.niyud.co.il / niyud.co.il (AAM)
  First check the login user (Verify token(if already saved at local), or get token from  user.niyud.co.il_(return if token have found via cookies) Else redirect to login user.niyud.co.il_)
  If user login is verified redirect to the admin dashboard


  