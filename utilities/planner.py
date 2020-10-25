import inquirer

# NOTE: Here is where we will plan to get settings and sequence imputs to rewrite settings file.
questions = [
  inquirer.List('size',
                message="What size do you need?",
                choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
            ),
]
answers = inquirer.prompt(questions)