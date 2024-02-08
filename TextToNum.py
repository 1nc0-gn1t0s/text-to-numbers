import sys
import sqlite3

from text_to_num import alpha2digit
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox


class Start(QMainWindow):
    """
    Это класс для открытия стартового окна с двумя кнопками: 'начать работу' и 'посмотреть инструкцию.'
    """
    def __init__(self):
        super(Start, self).__init__()

        uic.loadUi('start.ui', self)  # Подключаем ui-файл, в котором находится интерфейс стартового окна.

        # Подключаем события (нажатия кнопок) с соответствующими им функциями.
        self.start.clicked.connect(self.start_work)
        self.read.clicked.connect(self.read_instruction)

    def start_work(self):
        """
        Функция, при срабатывании которой закрывается стартовое окно и открывается основное окно с калькулятором.
        Вызывается при нажатии кнопки 'начать работу'.
        :return: None
        """
        self.ex = Calculator()
        self.ex.show()
        self.close()

    def read_instruction(self):
        """
        Функция, при срабатывании которой открывается окно с инструкцией использования калькулятора.
        Вызывается при нажатии кнопки 'прочитать инструкцию'.
        :return: None
        """
        self.ex = Instruction()
        self.ex.show()


class Instruction(QMainWindow):
    """
    Класс для открытия окна с инструкцией.
    """
    def __init__(self):
        super(Instruction, self).__init__()

        uic.loadUi('instruction.ui', self)
        # Подключаемся к ui-файлу, в котором находится текстовое поле
        # для вывода инструкции.

        with open('instruction_for_calculator.txt', 'r', encoding="utf-8") as file:
            text = file.read()
            self.PlaceForInstruction.setPlainText(text)  # Вставляем текст из файла в поле для инструкции.


class History(QMainWindow):
    """
    Класс для открытия окна с историей запросов. Содержит кнопку 'отчистить историю'.
    """
    def __init__(self):
        super(History, self).__init__()

        uic.loadUi('history.ui', self)
        # Подключаем ui-файл, в котором есть поле для вывода таблицы с историей запросов
        # и кнопка 'отчистить историю'.

        self.con = sqlite3.connect("Text_to_num.db")
        # Подключаем базу данных, в которой хранятся две таблицы: одна с математическими операциями
        # в текстовом виде и в математической записи, вторая - с историей запросов.

        self.select_data()  # Выполняем функцию, которая записывает содержимое

        # Подключаем функцию, которая будет выполняться при нажатии кнопки 'отчистить историю'.
        self.clearHistory.clicked.connect(self.clear_history)

    def select_data(self):
        """
        Функция для заполнения таблицы с историей запросов.
        :return: None
        """
        # Для начала нам нужно заполнить размеры таблицы. Количество столбцов у нас постоянное, 3, а вот
        # количество строк (записей из истории запросов) варьируется. Поставим его изначально как 0.
        self.HistoryTable.setColumnCount(3)
        self.HistoryTable.setRowCount(0)
        # Даем названия столбцам.
        self.HistoryTable.setHorizontalHeaderLabels(['Ввод', 'Математическое выражение', 'Ответ'])
        res = self.con.cursor().execute("""SELECT * FROM History""").fetchall()
        # res - это список кортежей с содержанием базы данных (один кортеж - одна строка).
        for i, row in enumerate(res):
            self.HistoryTable.setRowCount(self.HistoryTable.rowCount() + 1)
            # Выставляем номер строки в таблице. Для этого мы смотрим, сколько уже строк есть, и прибавляем один к их
            # количеству.
            for j, elem in enumerate(row):
                # i - номер ряда, который мы заполняем, j - номер столбца. Передаем их и сам элемент,
                # который нужно вписать в таблицу на место (j, i), в функцию 'setItem()'.
                self.HistoryTable.setItem(i, j, QTableWidgetItem(str(elem)))
        self.HistoryTable.resizeColumnsToContents()  # Подстраиваем ширину ячеек под текст в них.

    def clear_history(self):
        """
        Функция для отчистки истории. Вызывается при нажатии на кнопку 'отчистить историю'.
        :return: None
        """
        self.con.cursor().execute("""DELETE FROM History""")  # Удаляем все записи из базы данных.
        self.con.commit()  # Подтверждаем изменения.
        self.select_data()
        # Заполняем таблицу заново (заполняем, соответственно, ничем, таблица останется пустой,
        # но если бы мы не совершали здесь эту функцию, то визуальных изменений в таблице не произошло бы сразу
        # (только при повторном открытии)).

    def closeEvent(self, event):
        """
        Функция для закрытия соединения с базой данных при закрытии окна.
        :param event: Событие (закрытие окна).
        :return: None
        """
        self.con.close()


class Calculator(QMainWindow):
    """
    Класс для основного окна с калькулятором.
    """
    def __init__(self):
        super(Calculator, self).__init__()

        uic.loadUi('text_to_num.ui', self)
        # Подключаем ui-файл с интерфейсом для калькулятора.

        self.text = ''  # В будущем в этой переменной будет храниться результат вычисления.

        # Подключаем кнопки к соответствующим им функциям.
        # look_history - для открытия окна с историей запросов,
        # clear - для отчистки форм ввода и вывода текста,
        # if_input - для отчистки поля с ответом и поля с численным представлением прошлого запроса при новом вводе,
        # count - для подсчета результата,
        # look_answer - для просмотра ответа.
        self.answer.clicked.connect(self.look_answer)
        self.input.textChanged.connect(self.if_input)
        self.numbers.clicked.connect(self.count)
        self.clearAll.clicked.connect(self.clear)
        self.history.clicked.connect(self.look_history)

    def look_history(self):
        """
        Функция для открытия окна с историей запросов. Вызывается при нажатии кнопки 'Посмотреть историю запросов'.
        :return: None
        """
        self.ex = History()
        self.ex.show()

    def clear(self):
        """
        Функция для отчистки форм ввода и вывода текста. Вызывается при нажатии кнопки 'Отчистить все'.
        :return: None
        """
        self.numInput.clear()
        self.output.clear()
        self.input.clear()

    def if_input(self):
        """
        Функция для отчистки поля с ответом и поля с численным представлением прошлого запроса.
        Вызывается при новом вводе.
        :return: None
        """
        self.numInput.clear()
        self.output.clear()
        self.text = ''

    def count(self):
        """
        Функция для перевода текста в более 'математический' вид и подсчета результатов.
        Вызывается при нажатии кнопки 'Посмотреть в числах'.
        :return: None
        """
        # text_input - ввод пользователя,
        # text_num - ввод пользователя в 'математическом' виде,
        # self.text - ответ.
        text_input = self.input.toPlainText()  # Забираем текст из поля ввода.
        text_num = alpha2digit(text_input, "ru")  # Переводим числа в тексте в числовую запись.

        con = sqlite3.connect("Text_to_num.db")
        # Подключаем базу данных, в которой хранятся две таблицы: одна с математическими операциями
        # в текстовом виде и в математической записи, вторая - с историей запросов.
        cur = con.cursor()
        rus_signs = [n[0] for n in cur.execute("SELECT Rus FROM MathOperations").fetchall()]
        rus_signs.reverse()
        # Если бы не было реверса, то rus_signs был бы равен ['плюс', 'минус', 'умножить на', 'поделить на',
        # 'в степени', 'найти остаток от деления на', 'левая скобка', 'правая скобка', 'целочисленно поделить на'],
        # то есть 'целочисленно поделить на' стоял бы после 'поделить на' и, соответственно, менялся бы на
        # 'целочисленно /', так как при переборе элементов rus_signs обычное деление встречалось бы раньше.
        # rus_signs - это список всех математических операций в текстовой (не-математической) записи.
        for i in rus_signs:
            if i in text_num:
                # Заменяем все вхождения элементов списка rus_signs на математические операции.
                text_num = text_num.replace(i, cur.execute(f"""SELECT Sign FROM MathOperations 
                WHERE Rus = '{i}'""").fetchone()[0])
        try:
            self.text = eval(text_num)  # Записываем в self.text результат вычислений.
        except ZeroDivisionError:  # Если пользователь захочет поделить на ноль, то выводим ошибку.
            self.text = 'На ноль делить нельзя!'
            error = QMessageBox()
            error.setWindowTitle('Ошибка')
            error.setText('На ноль делить нельзя!')
            error.setIcon(QMessageBox.Warning)
            error.setStandardButtons(QMessageBox.Ok)
            _ = error.exec_()
        con.execute(f"""INSERT INTO History VALUES ('{text_input}', '{text_num}', '{self.text}')""")
        # Добавляем запрос в базу данных.
        con.commit()
        con.close()
        self.numInput.setText(text_num)  # Выводим запрос в 'математической' записи.

    def look_answer(self):
        """
        Функция для вывода результата.
        :return: None
        """
        self.output.setText(str(self.text))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec())
