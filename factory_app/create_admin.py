"""
Script para criar utilizador admin inicial
Execute: python create_admin.py
"""
import sys
from sqlalchemy.orm import Session
from getpass import getpass

from config.database import SessionLocal, engine
from app.models.user import User, UserRole
from utils.security import get_password_hash


def create_admin_user():
    """Cria utilizador admin inicial"""
    db: Session = SessionLocal()

    try:
        # Verificar se já existe algum admin
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()

        if existing_admin:
            print(f"❌ Já existe um utilizador admin: {existing_admin.username}")
            print("   Se perdeu a senha, contacte o administrador do sistema.")
            return False

        print("=" * 60)
        print("CRIAR UTILIZADOR ADMINISTRADOR INICIAL")
        print("=" * 60)
        print()

        # Solicitar dados
        username = input("Username (admin): ").strip() or "admin"
        email = input("Email (admin@factory.local): ").strip() or "admin@factory.local"
        full_name = input("Nome Completo (Administrador): ").strip() or "Administrador"

        # Solicitar senha com confirmação
        while True:
            password = getpass("Senha: ")
            if len(password) < 6:
                print("❌ Senha deve ter pelo menos 6 caracteres")
                continue

            password_confirm = getpass("Confirmar Senha: ")
            if password != password_confirm:
                print("❌ Senhas não coincidem. Tente novamente.")
                continue

            break

        # Criar utilizador
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print()
        print("✅ Utilizador admin criado com sucesso!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Role: ADMIN")
        print()
        print("Pode agora fazer login na aplicação.")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Função principal"""
    print()
    print("Factory Work Tracking System - Admin Setup")
    print()

    # Verificar conexão com BD
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Conexão com base de dados OK")
        print()
    except Exception as e:
        print(f"❌ Erro ao conectar com base de dados: {e}")
        print()
        print("Verifique:")
        print("  1. SQL Server está a correr")
        print("  2. Configurações em config/settings.py estão corretas")
        print("  3. Base de dados 'factory_db' existe")
        print("  4. Tabelas foram criadas (execute create_tables.sql)")
        sys.exit(1)

    # Criar admin
    success = create_admin_user()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
