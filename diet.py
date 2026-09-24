def bmi_calculator(weight,height):
    bmi=weight/((height/100)**2)
    return bmi

def bmr_calculator(weight,height,age,gender):
  if gender=='Male':
     bmr=(10*weight)+(6.25*height)-(5*age)+5
     return bmr

  else:
     bmr=(10*weight)+(6.25*height)-(5*age)-161
     return bmr

def tdee_calculator(bmr,activity):
   activity_factor={"sedentary":1.20,
                    "lightly active":1.375,
                    "moderately active":1.55,
                    "very active":1.725,
                    "extra active":1.90}
   tdee=bmr*activity_factor[activity]
   return round(tdee,2)
def calorie_target(tdee,aim):
   if aim=='weight maintain':
      calorie=tdee
   elif aim==' weight loss':
      calorie=tdee-400
   elif aim=='weight gain':
      calorie=tdee+300
      return round(calorie,2)

# print(bmi_calculator(60,150))
# bmr=bmr_calculator(60,150,20,'male')
# tdee=tdee_calculator(bmr,'sedentary')
# print(calorie_target(tdee,'weight loss'))