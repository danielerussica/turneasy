import pulp
from pulp import LpMinimize, LpProblem, LpVariable, lpSum

# Definizione dei dati
employees = ["Alice", "Bob", "Charlie", "David"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
shifts_per_day = 3

# Disponibilità dei dipendenti
availability = {
    "Alice": {"Monday": [1, 1, 0], "Tuesday": [1, 1, 1], "Wednesday": [1, 1, 0], "Thursday": [1, 1, 1], "Friday": [1, 0, 1], "Saturday": [0, 1, 1], "Sunday": [1, 1, 1]},
    "Bob": {"Monday": [1, 1, 1], "Tuesday": [1, 1, 0], "Wednesday": [1, 1, 1], "Thursday": [1, 0, 1], "Friday": [1, 1, 1], "Saturday": [1, 1, 0], "Sunday": [0, 1, 1]},
    "Charlie": {"Monday": [1, 0, 1], "Tuesday": [1, 1, 1], "Wednesday": [1, 1, 1], "Thursday": [1, 1, 0], "Friday": [0, 1, 1], "Saturday": [1, 1, 1], "Sunday": [1, 0, 1]},
    "David": {"Monday": [1, 1, 1], "Tuesday": [1, 0, 1], "Wednesday": [0, 1, 1], "Thursday": [1, 1, 1], "Friday": [1, 1, 0], "Saturday": [1, 1, 1], "Sunday": [1, 1, 1]},
}

# Livello di abilità dei dipendenti (ad esempio, da 1 a 5)
skill_levels = {
    "Alice": 3,
    "Bob": 4,
    "Charlie": 2,
    "David": 5,
}

# Numero di dipendenti richiesti e baseline di abilità per ogni turno
turn_requirements = {
    "Monday": [2, 3, 2],
    "Tuesday": [2, 2, 3],
    "Wednesday": [3, 2, 2],
    "Thursday": [2, 3, 2],
    "Friday": [3, 2, 3],
    "Saturday": [2, 3, 2],
    "Sunday": [3, 2, 3],
}

skill_baseline = {
    "Monday": [6, 8, 6],
    "Tuesday": [6, 6, 8],
    "Wednesday": [8, 6, 6],
    "Thursday": [6, 8, 6],
    "Friday": [8, 6, 8],
    "Saturday": [6, 8, 6],
    "Sunday": [8, 6, 8],
}

# Coppie di dipendenti che non possono lavorare assieme
forbidden_pairs = [("Alice", "Bob"), ("Charlie", "David")]

# Creazione del problema di ottimizzazione
prob = LpProblem("RosterScheduling", LpMinimize)

# Variabili di decisione: x[e][d][s] è 1 se il dipendente 'e' è assegnato al turno 's' del giorno 'd', altrimenti 0
x = LpVariable.dicts("shift", (employees, days, range(shifts_per_day)), 0, 1, cat='Binary')

# Funzione obiettivo: minimizzare il numero di turni non coperti
prob += lpSum([1 - x[e][d][s] for e in employees for d in days for s in range(shifts_per_day)])

# Constraints: ogni turno deve essere coperto dal numero richiesto di dipendenti
for d in days:
    for s in range(shifts_per_day):
        prob += lpSum([x[e][d][s] for e in employees]) == turn_requirements[d][s]

# Constraints: rispetto delle disponibilità dei dipendenti
for e in employees:
    for d in days:
        for s in range(shifts_per_day):
            prob += x[e][d][s] <= availability[e][d][s]

# Constraints settimanali: ogni dipendente deve avere almeno un giorno libero
for e in employees:
    prob += lpSum([x[e][d][s] for d in days for s in range(shifts_per_day)]) <= 6 * shifts_per_day

# Constraints permanenti: ogni dipendente deve lavorare almeno 3 turni a settimana
for e in employees:
    prob += lpSum([x[e][d][s] for d in days for s in range(shifts_per_day)]) >= 3

# Constraints: ogni turno deve soddisfare la baseline di abilità
for d in days:
    for s in range(shifts_per_day):
        prob += lpSum([x[e][d][s] * skill_levels[e] for e in employees]) >= skill_baseline[d][s]

# Constraints: forbidden pairs
for e1, e2 in forbidden_pairs:
    for d in days:
        for s in range(shifts_per_day):
            prob += x[e1][d][s] + x[e2][d][s] <= 1

# Risoluzione del problema
prob.solve()

# Output della soluzione in formato trasposto
print("Roster settimanale (ogni giorno con i turni e i dipendenti assegnati):")
for d in days:
    print(f"{d}:")
    for s in range(shifts_per_day):
        assigned_employees = [e for e in employees if x[e][d][s].varValue == 1]
        if assigned_employees:
            print(f"  Turno {s+1}: {', '.join(assigned_employees)}")
        else:
            print(f"  Turno {s+1}: Nessuno assegnato")
