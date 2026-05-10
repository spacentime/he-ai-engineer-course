'''
Create a base class called "Animal" with a method "sound" that returns a generic sound.
Then, create two subclasses "Dog" and "Cat" that inherit from the "Animal" class. 
Override the "sound" method in each subclass to return a specific sound for dogs and cats. 
Finally, create instances of both subclasses and call their "sound" methods to see the output.

'''

class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        return f"{self.name} is eating."

    def sleep(self):
        return f"{self.name} is sleeping."    

    def sound(self):
        return "I am an animal"
    
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)

    def sound(self):
        return "Woof!"
    
    def fetch(self):
        return "I am fetching the ball!"
    
class Cat(Animal):
    def __init__(self, name):
        super().__init__(name)
        
    def sound(self):
        return "Meow!"
    
    def scratch(self):
        return "I am scratching the furniture!"
    
cat = Cat("Whiskers")
print(cat.name)  # Output: Whiskers
print(cat.sound())  # Output: Meow!
print(cat.scratch())  # Output: I am scratching the furniture!
print(cat.eat())  # Output: Whiskers is eating.
print(cat.sleep())  # Output: Whiskers is sleeping. 

dog = Dog("Buddy")
print(dog.name)  # Output: Buddy    
print(dog.sound())  # Output: Woof!
print(dog.fetch())  # Output: I am fetching the ball!
print(dog.eat())  # Output: Buddy is eating.
print(dog.sleep())  # Output: Buddy is sleeping.


