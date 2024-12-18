Here’s the improved version of your document with the requested changes and additional context about the software:

---

# **Wasooli**: A DjangoRestFramework-Based Solution for Monthly Fee Collection

Wasooli is a Django-based application designed to replace manual vouchers traditionally used for monthly fee collection. This project provides a streamlined and efficient way to manage collections using a modern web interface.

---

## **Getting Started**

### **Clone the Project**

You can clone the repository using either HTTPS or SSH:

#### **_HTTPS:_**

```bash
git clone https://github.com/abdullahzulfiqar653/SimpleBoilerplateDjango.git
```

#### **_SSH:_**

```bash
git clone git@github.com:abdullahzulfiqar653/SimpleBoilerplateDjango.git
```

---

## **Setup Instructions**

Follow these steps to set up the project on your local machine.

### **Step 1: Install Python**

Make sure Python 3.11.7 is installed on your local machine. You can download it from the [official Python website](https://www.python.org/).

---

### **Step 2: Install Poetry**

Poetry is used to manage dependencies and the virtual environment for the project. Install it using the appropriate command for your operating system:

#### **Windows:**

```bash
pip install poetry
```

#### **macOS/Linux:**

```bash
pip3 install poetry
```

---

### **Step 3: Set Up the Environment and Install Dependencies**

1. **Install Packages:**
   Open a terminal in the `SimpleBoilerplateDjango` directory and run the following command to create a virtual environment and install the required dependencies:

   ```bash
   poetry install
   ```

2. **Activate the Environment:**
   After the installation is complete, activate the environment using this command:

   ```bash
   poetry shell
   ```

---

### **Step 4: Configure Environment Variables**

Create a `.env` file in the main source directory (at the same level as `manage.py` and `.env.example`). Use `.env.example` as a reference to set up all the required environment variables.

---

### **Step 5: Run the Application**

Make sure the virtual environment is activated and that you are in the `SimpleBoilerplateDjango` directory. Start the Django development server using this command:

```bash
python manage.py runserver
```

---

## **Key Features of Wasooli**

- **Automated Voucher Management:** Simplify and digitize the collection of monthly fees.  
- **Django-Powered API:** Built with Django to provide robust and scalable backend support.  
- **Streamlined Workflow:** No more manual paperwork—manage collections efficiently through a centralized system.

---

Feel free to reach out for further support or contributions to the Wasooli project.
