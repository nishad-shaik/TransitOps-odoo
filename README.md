TransitOps — Smart Transport Operations Platform

A centralized platform for managing the full lifecycle of transport operations vehicle registry, driver management, trip dispatch, maintenance, fuel & expense tracking, and operational analytics — built to replace spreadsheet-driven fleet management.






Tech stack


Adjust this section to match what you actually used — placeholders below assume a common MERN-ish setup.




Frontend: Html,Css,Js
Backend: Python(flask)
Database: MySQL
Auth: JWT-based, Role-Based Access Control (RBAC)



Roles

RoleAccessFleet ManagerVehicle CRUD, maintenance, dashboard, reportsDriverCreate/dispatch trips, view active deliveriesSafety OfficerDriver compliance, license validity, safety scoresFinancial AnalystExpenses, fuel cost, maintenance cost, profitability (read-mostly)AdminUser & role management

Core features implemented


 Secure login with RBAC
 Dashboard with fleet KPIs (Active/Available Vehicles, In Maintenance, Active/Pending Trips, Drivers On Duty, Fleet Utilization %)
 Vehicle Registry (CRUD, unique registration number)
 Driver Management (CRUD, license tracking, safety score)
 Trip lifecycle: Draft → Dispatched → Completed → Cancelled, with full validation
 Maintenance workflow with automatic vehicle status transitions
 Fuel & expense logging with automatic cost rollup per vehicle
 Reports: Fuel Efficiency, Fleet Utilization, Operational Cost, Vehicle ROI
 CSV export
 PDF export (optional, not implemented)
 Dark mode (bonus, not implemented)
 Email reminders for expiring licenses (bonus, not implemented)


Business rules enforced


Vehicle registration numbers and driver license numbers are unique.
Retired or In Shop vehicles never appear in the trip dispatch dropdown.
Suspended drivers or drivers with an expired license cannot be assigned to a trip.
A vehicle or driver already On Trip cannot be assigned to a second trip.
Cargo weight cannot exceed the assigned vehicle's max load capacity.
Dispatching a trip sets both vehicle and driver to On Trip; completing or cancelling restores both to Available.
Opening a maintenance record automatically sets the vehicle to In Shop and removes it from dispatch; closing it restores Available (unless the vehicle is Retired).





Database schema

See TransitOps_Design_Doc.md for the full ERD, field-level schema, and workflow breakdown.

Entities: users, drivers, vehicles, trips, maintenance_logs, fuel_logs, expenses.

Getting started

bash# clone
git clone 
cd transitops

# backend
cd server
npm install
cp .env.example .env   # set DATABASE_URL, JWT_SECRET
npm run migrate
npm run seed            # optional: sample vehicles/drivers/trips
npm run dev

# frontend
cd ../client
npm install
npm run dev

Environment variables

VariableDescriptionDATABASE_URLPostgreSQL connection stringJWT_SECRETSecret used to sign auth tokensPORTBackend port (default 4000)

Default seeded logins

RoleEmailPasswordFleet Managerfleetmanager@transitops.devpassword123Driverdriver@transitops.devpassword123Safety Officersafety@transitops.devpassword123Financial Analystfinance@transitops.devpassword123


Replace with your actual seed data before submission.



API overview

MethodRouteDescriptionRolesPOST/api/auth/loginLogin, returns JWTAllGET/api/dashboardKPI summaryAllGET/POST/api/vehiclesList / register vehicleFleet ManagerPATCH/api/vehicles/:idUpdate vehicleFleet ManagerGET/POST/api/driversList / add driverSafety Officer, Fleet ManagerGET/POST/api/tripsList / create trip (Draft)Driver, Fleet ManagerPOST/api/trips/:id/dispatchDispatch trip (runs validations)Driver, Fleet ManagerPOST/api/trips/:id/completeComplete tripDriver, Fleet ManagerPOST/api/trips/:id/cancelCancel dispatched tripDriver, Fleet ManagerGET/POST/api/maintenanceList / open maintenance logFleet ManagerPATCH/api/maintenance/:id/closeClose maintenance logFleet ManagerGET/POST/api/fuel-logsList / add fuel logFleet Manager, Financial AnalystGET/POST/api/expensesList / add expenseFleet Manager, Financial AnalystGET/api/reportsFuel efficiency, utilization, cost, ROIFinancial Analyst, Fleet ManagerGET/api/reports/export.csvCSV export of current report viewFinancial Analyst, Fleet Manager


Update this table to match your actual implemented routes before submission — judges will spot-check it.



Demo script (suggested walkthrough order)


Log in as Fleet Manager → show dashboard KPIs.
Register vehicle Van-05 (500 kg capacity) → show it appear in registry.
Add driver Alex with valid license.
Create a trip, cargo 450 kg → dispatch → show vehicle/driver flip to On Trip and disappear from selection pools.
Attempt to over-load or double-assign to demonstrate validation errors.
Complete the trip → show both revert to Available, odometer updates.
Open a maintenance log on the vehicle → show it vanish from dispatch (In Shop).
Close maintenance → vehicle returns to Available.
Log a fuel entry and an expense → switch to Financial Analyst login → show cost rollup and ROI on the reports page.
Export CSV.
