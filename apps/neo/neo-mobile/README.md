# neo-mobile

## creating new project

* npx create-expo-app@latest
* npm install -g eas-cli
* eas login
* cd src && eas build:configure
* eas build --local --platform android --profile development

## keycloak conditional access
1. Create a Group or Role for Allowed Users
Go to Users → Groups or Users → Roles in the Keycloak admin console.
Create a group (e.g., allowed-users) or a role (e.g., can-login).
Assign this group/role to the users who should be able to log in.
2. Copy the Default Authentication Flow
Go to Authentication → Flows.
Find the Browser flow (or the flow your client uses).
Click Copy to duplicate it (e.g., name it Browser with Group Check).
3. Add a Condition to the Flow
In your new flow, click Add execution.
Choose Conditional Group (for groups) or Conditional Role (for roles).
Set it to REQUIRED.
Click the gear icon to configure it, and enter the group or role you created.
4. Set Your Client to Use the New Flow
Go to Clients → [your-client] → Authentication Flow Overrides.
Set the Browser Flow to your new flow.
5. Test
Only users in the specified group/role will be able to log in. Others will be denied access.
