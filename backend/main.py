nome = (input("Digite sua materia: "))
horas = (int(input("Digite a quantidade de horas: ")))
progresso = (int(input("Digite o progresso em porcentagem: ")))

print(f"Materia: {nome}")
print(f"Horas: {horas}")
print(f"Progresso: {progresso}%")



def verificar_progresso(progresso):
        if progresso >= 100:
            print("Parabéns! Você concluiu a matéria.")
        elif progresso >= 75:
                print("Você está quase lá! Continue se esforçando.")
        elif progresso >= 60:
            print("Você está progredindo bem! Continue estudando.")        
        elif progresso >= 50:
            print("Bom trabalho! Você está progredindo bem.")
        elif progresso >= 42:
            print("Você está indo bem neste nivel! Continue assim.")    
        elif progresso >= 35:
            print("Ótima progresso! Continue estudando para alcançar o próximo nível.")    
        elif progresso >= 25:
            print("Você está no caminho certo! Continue estudando.")
        elif progresso >= 10:
            print("Está indo bem! Continue assim.")    
        elif progresso >= 5:
            print("Você está começando a aprender. Continue se dedicando!")    
        elif progresso >= 0:
                print("Não desanime! Continue se dedicando aos estudos.")
        else:
            print("Voce ainda não começou a estudar. Vamos começar agora!")




def calcular_nivel(progresso):
    
    if progresso >= 100:
        return "Concluído"
    elif progresso >= 90:
        print("Você está no nível de Domínio prático.")
        return "Domínio prático"
    elif progresso >= 80:
        print("Você está no nível Python Avançado.")
        return "Python Avançado"
    elif progresso >= 70:
        print("Você está aprendendo orientação a objetos.")
        return "Orientação a objetos"
    elif progresso >= 60:
        print("Você está no nível Python Intermediário.")
        return "Python Intermediário"
    elif progresso >= 50:
        print("Você está aprendendo Funções e organização.")
        return "Funções e organização"
    elif progresso >= 40:
        print("Você está aprendendo Manipulação de dados.")
        return "Manipulação de dados"
    elif progresso >= 30:
        print("Você está aprendendo Controle de fluxo.")
        return "Controle de fluxo"
    elif progresso >= 20:
        print("Você está aprendendo Lógica de programação.")
        return "Lógica de programação"
    elif progresso >= 10:
        print("Você está no nível Básico.")
        return "Fundamentos Básicos"
    elif progresso >= 0:
        print("Você está no Primeiro contato com a matéria.")
        return "Iniciante Absoluto"




if progresso < 0 or progresso > 100:
    print("Erro: O progresso deve estar entre 0 e 100%.")
else:
    verificar_progresso(progresso)
    nivel_atual = calcular_nivel(progresso)
print(f"Nível atual: {nivel_atual}")

