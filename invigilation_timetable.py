import pandas as pd 
import numpy as np
import random

# Define class
class Invigilator:
    def __init__(self, initial, time_remain, unavailable_datetime=None):
        self.initial = initial
        self.time_remain = time_remain
        self.unavailable_datetime = pd.to_datetime(unavailable_datetime, format='%d/%m/%y %H:%M')
        self.invigilations = []
    
    def assign(self, Exam):
        self.invigilations.append(Exam)
        self.time_remain -= Exam.duration
    
    def unassign(self, Exam):
        if Exam in self.invigilations:
            self.invigilations.remove(Exam)
            self.time_remain += Exam.duration
        else:
            pass

class Exam:
    def __init__(self, subject, form, no_of_class, date, start_time, duration):
        self.subject = subject
        self.form = form
        self.no_of_class = no_of_class
        self.date = date
        self.start_datetime = pd.to_datetime(start_time, format='%H:%M')
        self.start_time = self.start_datetime.time()
        self.duration = duration
        self.end_time = (self.start_datetime + pd.to_timedelta(self.duration, unit='min')).time()
        self.invigilators = []

    def allocate_to(self, Invigilator):
        self.invigilators.append(Invigilator)
        Invigilator.assign(self)
    
    def remove_invig(self, Invigilator):
        if Invigilator in self.invigilators:
            self.invigilators.remove(Invigilator)
            Invigilator.unassign(self)

    def inv_initials(self):
        initials = []
        for invigilator in self.invigilators: 
            initials.append(invigilator.initial)
        return initials

    def isOverlap(self,AnotherExam):
        if (self.start_time <= AnotherExam.start_time <= self.end_time) or (
            AnotherExam.start_time <= self.start_time <= AnotherExam.end_time):
            return True
        else:
            return False

# Import data
invig_df = pd.read_csv('invigilators.csv')
exams_df = pd.read_csv('exam_info.csv')

# Covert the data into a list of the class created
invigilators = []

for index, initial in enumerate(invig_df['initial']):
    invigilator = Invigilator(initial, time_remain=invig_df['time_remain'].iloc[index])
    invigilators.append(invigilator)

exams = []

for index, subject in enumerate(exams_df['subject']):
    exam = Exam(subject=subject, form=exams_df['form'].iloc[index],
                no_of_class=exams_df['no_of_class'].iloc[index], 
                date=exams_df['date'].iloc[index],
                start_time=exams_df['start_time'].iloc[index],
                duration=exams_df['duration'].iloc[index])
    exams.append(exam)

# TODO: Allocate the invigilation to invigilators
def next_missing_invig(exams):
    for index, exam in enumerate(exams):
        if len(exam.invigilators) < exam.no_of_class:
            return index
    return None

def allocate(exams, invigilators):
    next = next_missing_invig(exams)
    if (next != 0 and not next):
        return True
    else:
        index = next


    
    for ran_invi in random.sample(invigilators, len(invigilators)):
        if isValid(exams[index], ran_invi):
            exams[index].allocate_to(ran_invi)

            # Debugging
            if len(exams[index].invigilators) == exams[index].no_of_class:
                print(exams[index].subject, end=': ')

                for invi in exams[index].invigilators:
                    if exams[index].invigilators.index(invi) == len(exams[index].invigilators)-1:
                        print(invi.initial)
                    else:
                        print(invi.initial, end=', ')

            if allocate(exams, invigilators):
                return exams, invigilators

            exams[index].remove_invig(ran_invi)
    return False

# TODO: Check if the allocation is valid
def isValid(Exam, Invigilator):
    if Invigilator.time_remain < Exam.duration:
        return False
    if Invigilator in Exam.invigilators:
        return False
    for invigilation in Invigilator.invigilations:
        if invigilation.date == Exam.date:
            if invigilation.isOverlap(Exam):
                return False
    
    return True



allocate(exams, invigilators)

for exam in exams:
    print('form', exam.form, exam.subject, end=': ') 
    for inv in exam.invigilators:
        if exam.invigilators.index(inv) == len(exam.invigilators)-1:
            print(inv.initial)
        else:
            print(inv.initial, end=', ')
# for invigilator in invigilators:
    # print(f'{invigilator.initial}: {invigilator.time_remain}')

# TODO: Export the generated list

def export(exams):
    exams_dict = {'form':[], 'subject':[], 'date':[], 'start_time':[], 'end_time':[], 'invigilator_1':[], 
                  'invigilator_2':[], 'invigilator_3':[], 'invigilator_4':[], 'invigilator_5':[]}
    for exam in exams:
        exams_dict['form'].append(exam.form)
        exams_dict['subject'].append(exam.subject)
        exams_dict['date'].append(exam.date)
        exams_dict['start_time'].append(exam.start_time.strftime('%H:%M'))
        exams_dict['end_time'].append(exam.end_time.strftime('%H:%M'))
        for index, initial in enumerate(exam.inv_initials()):
            exams_dict[f'invigilator_{index+1}'].append(exam.inv_initials()[index])
        for index in range(len(exam.inv_initials()), 5):
            exams_dict[f'invigilator_{index+1}'].append(None)

    export_exams = pd.DataFrame.from_dict(data=exams_dict).to_csv('invigilations.csv')
    return export_exams

# export_exams = export(exams)
