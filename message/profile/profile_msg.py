def profile_message(user):

    return f"""
<b>👤 USER PROFILE</b>

<b>🆔 ID :</b> <code>{user.id}</code>
<b>👤 Name :</b> {user.first_name}
<b>🔗 Username :</b> @{user.username if user.username else "None"}

<b>📊 More profile features coming soon...</b>
"""